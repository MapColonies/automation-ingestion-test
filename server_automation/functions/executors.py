# pylint: disable=line-too-long, invalid-name, fixme
"""This module provide test full functionality """
import logging
import time
import json
import glob
import os
import shutil
from pathlib import Path
import xmltodict

from mc_automation_tools import common as common
from mc_automation_tools import shape_convertor, base_requests
from mc_automation_tools import s3storage as s3
from mc_automation_tools.ingestion_api import job_manager_api
from discrete_kit.functions import metadata_convertor
from mc_automation_tools.ingestion_api import azure_pvc_api
from mc_automation_tools.models import structs
from shapely.geometry import Polygon
from server_automation.configuration import config
from server_automation.ingestion_api import (
    discrete_agent_api,
    discrete_directory_loader,
)
from server_automation.postgress import postgress_adapter
from server_automation.graphql import gql_wrapper
from server_automation.pycsw import pycsw_handler
from mc_automation_tools.validators import pycsw_validator, mapproxy_validator
from discrete_kit.validator.json_compare_pycsw import *

# from importlib.resources import path
FAILED_ = "Failed: "

_log = logging.getLogger("server_automation.function.executors")


def stop_watch():
    """
    This method stop and validate stop / status api of agent for watching
    :return: result dict: {state: bool, reason: str}
    """
    try:
        resp = discrete_agent_api.post_stop_watch()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {
                "state": False,
                "reason": f"Failed on getting watch status API: [{status_code}]:[{resp.content}]",
            }

        reason = json.loads(resp.content)
        if reason["isWatching"]:
            return {
                "state": False,
                "reason": f"Failed on stop watch via status API: [{json.loads(resp.content)}]",
            }
        resp = discrete_agent_api.get_watching_statuses()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {
                "state": False,
                "reason": f"Failed on getting watch status API after changing: [{status_code}]:[{resp.content}]",
            }

        return {"state": True, "reason": "isWatch=False - agent not watching"}
    except Exception as e:
        _log.error(f"Failed on stop watching process with error: [{str(e)}]")
        raise RuntimeError(f"Failed on stop watching process with error: [{str(e)}]")


def start_watch():
    """
    This method start and validate start or status api agent for watching
    :return: result dict: {state: bool, reason: str}
    """
    try:
        resp = discrete_agent_api.post_start_watch()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {
                "state": False,
                "reason": f"Failed on getting watch status API: [{status_code}]:[{resp.content}]",
            }

        reason = json.loads(resp.content)
        if not reason["isWatching"]:
            return {
                "state": False,
                "reason": f"Failed on start watch via status API: [{resp.content}]",
            }
        resp = discrete_agent_api.get_watching_statuses()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {
                "state": False,
                "reason": f"Failed on getting watch status API after changing: [{status_code}]:[{resp.content}]",
            }

        return {"state": True, "reason": "isWatch=True - agent on watching"}

    except Exception as e:
        _log.error(f"Failed on start watching process with error: [{str(e)}]")
        raise RuntimeError(f"Failed on start watching process with error: [{str(e)}]")


def init_watch_ingestion_src():
    """
    This method create test dedicated folder of source discrete for ingestion
    :param env:
    :return:
    """

    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        host = config.PVC_HANDLER_ROUTE
        api = config.PVC_WATCH_CREATE_DIR
        change_api = config.PVC_WATCH_UPDATE_SHAPE
        res = init_ingestion_src_pvc(
            True, host, api, change_api, update_tfw_url=config.PVC_CHANGE_WATCH_MAX_ZOOM
        )
        return res
    if config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        src = os.path.join(config.NFS_WATCH_ROOT_DIR, config.NFS_WATCH_SOURCE_DIR)
        dst = os.path.join(
            config.NFS_WATCH_ROOT_DIR,
            config.NFS_WATCH_ROOT_DIR,
            config.NFS_WATCH_DEST_DIR,
            common.generate_uuid(),
        )
        res = init_ingestion_src_fs(src, dst, watch=True)
        return res
    else:
        raise RuntimeError(f"Illegal environment value type: {config.SOURCE_DATA_PROVIDER.lower()}")


def delete_file_from_folder(path_to_folder, file_to_delete):
    pvc_handler = azure_pvc_api.PVCHandler(
        endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
    )

    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        resp = pvc_handler.delete_file_from_folder(path_to_folder, file_to_delete)
        # ToDo: Continue here
        if not resp.status_code == config.ResponseCode.Ok.value:
            raise RuntimeError(
                f"Failed access pvc on source data cloning with error: [{resp.text}] and status: [{resp.status_code}]"
            )
    if config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        _log.info(f"Deleting file - {file_to_delete} from folder")
        ret_folder = glob.glob(path_to_folder + "/**/" + file_to_delete, recursive=True)
        if not ret_folder:
            _log.error(f"{file_to_delete} not found in {path_to_folder}")
            raise RuntimeError(f"{file_to_delete} not found in {path_to_folder}")
        try:
            for folder in ret_folder:
                os.remove(folder)
                _log.info(f"{folder} have been deleted")
        except OSError as e:
            _log.error(f"error occurred , msg : {str(e)}")


def init_ingestion_src():
    """
    This module will init new ingestion source folder.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        res = init_ingestion_src_pvc(False)
        return res
    if config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        src = os.path.join(config.NFS_ROOT_DIR, config.NFS_SOURCE_DIR)
        dst = os.path.join(config.NFS_ROOT_DIR_DEST, config.NFS_DEST_DIR)
        try:
            res = init_ingest_nfs(src, dst, str(config.zoom_level_dict[config.MAX_ZOOM_TO_CHANGE]))
            # res = init_ingestion_src_fs(src, dst, str(config.zoom_level_dict[config.MAX_ZOOM_TO_CHANGE]), watch=False)
            return res
        except FileNotFoundError as e:
            raise e
        except Exception as e1:
            raise RuntimeError(
                f"Failed generating testing directory with error: {str(e1)}"
            )
    else:
        raise ValueError(f"Illegal environment value type: {config.SOURCE_DATA_PROVIDER.lower()}")


def delete_destination_folder(dst):
    try:
        folder_to_delete = os.path.dirname(dst)
        if os.path.exists(folder_to_delete):
            _log.info(f"Folder To Delete: {folder_to_delete}")
    except Exception as er:
        raise RuntimeError(f"Failed to find {folder_to_delete} folder")


def copy_file_from_src_to_dst(src, dst):
    try:
        create_folder_cmd = f"cp -r {src}/. {dst}"
        os.system(create_folder_cmd)
        if os.path.exists(dst):
            _log.info(f"Success copy and creation of test data on: {dst}")
        else:
            raise IOError("Failed on creating ingestion directory")

    except Exception as e2:
        _log.error(f"Failed copy files from {src} into {dst} with error: [{str(e2)}]")
        raise e2


def update_destination_shape_file(dst):
    try:
        # file = os.path.join(dst, config.SHAPES_PATH, config.SHAPE_METADATA_FILE)
        file = os.path.join(
            discrete_directory_loader.get_folder_path_by_name(dst, config.SHAPES_PATH),
            config.SHAPE_METADATA_FILE,
        )
        if config.FAILURE_FLAG:
            source_name = update_shape_fs_to_failure(file)
        else:
            source_name = update_shape_fs(file)
        _log.info(f"[{file}]:was changed resource name: {source_name}")
    except Exception as e:
        _log.error(f"Failed on updating shape file: {file} with error: {str(e)}")
        raise e
    return source_name


def update_shape_zoom_level(dst, zoom_level):
    if config.PVC_UPDATE_ZOOM:
        res = metadata_convertor.replace_discrete_resolution(
            dst, zoom_level, "tfw"
        )
        return res


# ToDo: Finish it
def init_ingest_nfs(src, dst, zoom_level):
    zoom_level = str(config.zoom_level_dict[config.MAX_ZOOM_TO_CHANGE])  # ToDo: Each test
    delete_destination_folder(dst)
    copy_file_from_src_to_dst(src, dst)
    update_resource_name = update_destination_shape_file(dst)
    zoom_level_resp = update_shape_zoom_level(dst, zoom_level)
    return {"ingestion_dir": dst, "resource_name": update_resource_name, "max_resolution": zoom_level_resp}


def init_ingestion_src_fs(src, dst, zoom_level, watch=False):
    """
    This module will init new ingestion source folder - for file system / NFS deployment.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    if watch:
        deletion_watch_dir = os.path.dirname(dst)
        if os.path.exists(deletion_watch_dir):
            # ToDo : Fix it
            print("Delete")
            # if config.DELETE_INGESTION_FOLDER:
            #     command = f"rm -rf {deletion_watch_dir}/*"
            #     os.system(command)
    else:
        deletion_watch_dir = dst
        if os.path.exists(dst):
            # ToDo : Fix it
            print(f"Delete {dst}")
            # if config.DELETE_INGESTION_FOLDER:
            #     command = f"rm -rf {deletion_watch_dir}"
            #     os.system(command)

    if not os.path.exists(src):
        raise FileNotFoundError(f"[{src}] directory not found")

    try:
        command = f"cp -r {src}/. {dst}"
        os.system(command)
        if os.path.exists(dst):
            _log.info(f"Success copy and creation of test data on: {dst}")
        else:
            raise IOError("Failed on creating ingestion directory")

    except Exception as e2:
        _log.error(f"Failed copy files from {src} into {dst} with error: [{str(e2)}]")
        raise e2

    try:
        # file = os.path.join(dst, config.SHAPES_PATH, config.SHAPE_METADATA_FILE)
        file = os.path.join(
            discrete_directory_loader.get_folder_path_by_name(dst, config.SHAPES_PATH),
            config.SHAPE_METADATA_FILE,
        )
        if config.FAILURE_FLAG:
            source_name = update_shape_fs_to_failure(file)
        else:
            source_name = update_shape_fs(file)
        _log.info(f"[{file}]:was changed resource name: {source_name}")
    except Exception as e:
        _log.error(f"Failed on updating shape file: {file} with error: {str(e)}")
        raise e

    if config.PVC_UPDATE_ZOOM:
        res = metadata_convertor.replace_discrete_resolution(
            dst, zoom_level, "tfw"
        )

    return {"ingestion_dir": dst, "resource_name": source_name, "max_resolution": res}


def init_ingestion_src_pvc(
        watch,
        host=config.PVC_HANDLER_ROUTE,
        create_api=config.PVC_CLONE_SOURCE,
        change_api=config.PVC_CHANGE_METADATA,
        update_tfw_url=config.PVC_CHANGE_MAX_ZOOM,
):
    """
    This module will init new ingestion source folder inside pvc - only on azure.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    pvc_handler = azure_pvc_api.PVCHandler(
        endpoint_url=config.PVC_HANDLER_ROUTE, watch=watch
    )

    try:
        # resp = azure_pvc_api.create_new_ingestion_dir(host, create_api)
        resp = pvc_handler.create_new_ingestion_dir()
        if not resp.status_code == config.ResponseCode.ChangeOk.value:
            raise RuntimeError(
                f"Failed access pvc on source data cloning with error: [{resp.text}] and status: [{resp.status_code}]"
            )
        msg = json.loads(resp.text)
        new_dir = msg["newDesination"]
        _log.info(
            f'[{resp.status_code}]: New test running directory was created from source data: {msg["source"]} into {msg["newDesination"]}'
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed access pvc on source data cloning with error: [{str(e)}]"
        )

    try:
        resp = pvc_handler.make_unique_shapedata()
        if not resp.status_code == config.ResponseCode.ChangeOk.value:
            raise RuntimeError(
                f"Failed access pvc on source data updating metadata.shp with error: [{resp.text}] and status: [{resp.status_code}]"
            )
        resource_name = json.loads(resp.text)["source"]
        _log.info(
            f"[{resp.status_code}]: metadata.shp was changed resource name: {resource_name}"
        )

    except Exception as e:
        raise RuntimeError(f"Failed access pvc on changing shape metadata: [{str(e)}]")

    if config.PVC_UPDATE_ZOOM:
        try:
            # ToDo: Fix Zoom
            resp = pvc_handler.change_max_zoom_tfw()
            if resp.status_code == config.ResponseCode.Ok.value:
                _log.info(
                    f'Max resolution changed successfully: [{json.loads(resp.text)["json_data"][0]["reason"]}]'
                )
            else:
                raise RuntimeError(
                    f'Failed on updating zoom level with error: [{json.loads(resp.text)["message"]} | {json.loads(resp.text)["json_data"]}]'
                )
        except Exception as e:
            raise IOError(f"Failed updating zoom max level with error: [{str(e)}]")
    return {"ingestion_dir": new_dir, "resource_name": resource_name}


def validate_source_directory(
        path=None, watch=False
):
    """
    This will validate that source directory include all needed files for ingestion
    :param path: None if working on azure - qa \\ dev with pvc
    :param env: default qa for azure running with pvc
    :return: True \\ False + response json
    """

    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        pvc_handler = azure_pvc_api.PVCHandler(
            endpoint_url=config.PVC_HANDLER_ROUTE, watch=watch
        )
        resp = pvc_handler.validate_ingestion_directory()
        content = json.loads(resp.text)
        if content.get("json_data"):
            return not content["failure"], content["json_data"]
        else:
            return content["failure"], "missing json data"
    elif config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        state, resp = discrete_directory_loader.validate_source_directory(path)
        content = ""
        content = resp["metadata"]
        if content:
            validation_tiff_dict, error_msg = validate_tiff_exists(
                path, resp["fileNames"]
            )
            assert (
                    all(validation_tiff_dict.values()) is True
            ), f" Failed: on following ingestion process [{error_msg}]"
            return True, content

        else:
            return False, "Failed on tiff validation"
        # return state, resp
    else:
        raise RuntimeError(f"illegal Environment name: [{config.SOURCE_DATA_PROVIDER.lower()}]")


def start_manual_ingestion(path, validation=True):
    """This method will trigger new process of discrete ingestion by provided path"""
    # validate directory include all needed files and data
    if validation:
        source_ok, body = validate_source_directory(path)
        if not source_ok:
            raise FileNotFoundError(
                f"Directory [{path}] with missing files / errors msg: [{body}]"
            )

    _log.info(f"Send ingestion request for dir: {path}")
    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        relative_path = path.split(config.PVC_ROOT_DIR)[1]
    if config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        relative_path = config.NFS_DEST_DIR

    resp = discrete_agent_api.post_manual_trigger(relative_path)
    status_code = resp.status_code
    content = resp.text
    _log.info(
        f"receive from agent - manual: status code [{status_code}] and message: [{content}]"
    )
    if not validation:
        return status_code, content, "empty"
    return status_code, content, body


def start_watch_ingestion(path):
    """This method will start watch agent and validate start of current job"""

    # validate directory include all needed files and data
    source_ok, body = validate_source_directory(path, watch=True)
    if not source_ok:
        raise FileNotFoundError(
            f"Directory [{path}] with missing files / errors msg: [{body}]"
        )

    _log.info(f"Init ingestion via watch start request for dir: {path}")

    resp = start_watch()
    watch_state = resp["state"]
    if not watch_state:
        raise RuntimeError(f"Failed on start watching with error:\n" f'{resp["reason"]}')

    _log.info(
        f'Receive from agent - watch status: [{watch_state}] and message: [{resp["reason"]}]'
    )

    return watch_state, resp["reason"], body


def follow_running_task(product_id, product_version, timeout=config.FOLLOW_TIMEOUT):
    """This method will follow running ingestion task and return results on finish"""

    t_end = time.time() + timeout
    running = True
    resp = gql_wrapper.get_job_by_product(
        product_id, product_version, host=config.GQK_URL
    )
    _log.info(resp)
    if not resp:
        raise RuntimeError(f"Job for {product_id}:{product_version} not found")

    while running:
        time.sleep(config.SYSTEM_DELAY // 4)
        job = gql_wrapper.get_job_by_product(
            product_id, product_version, host=config.GQK_URL
        )
        job_id = job["id"]
        status = job["status"]
        reason = job["reason"]
        tasks = job["tasks"]

        completed_task = sum(
            1 for task in tasks if task["status"] == config.JobStatus.Completed.name
        )
        _log.info(
            f"\nIngestion status of job for resource: {product_id}:{product_version} is [{status}]\n"
            f"finished tasks for current job: {completed_task} / {len(tasks)}"
        )

        if status == config.JobStatus.Completed.name:
            return {
                "status": status,
                "message": " ".join(["OK", reason]),
                "job_id": job_id,
            }
        elif status == config.JobStatus.Failed.name:
            return {
                "status": status,
                "message": " ".join([FAILED_, reason]),
                "job_id": job_id,
            }

        current_time = time.time()

        if t_end < current_time:
            return {
                "status": status,
                "message": " ".join(
                    [FAILED_, "got timeout while following job running"]
                ),
                "job_id": job_id,
            }


def follow_running_job_manager(
        product_id, product_version, timeout=config.FOLLOW_TIMEOUT
):
    """This method will follow running ingestion task and return results on finish"""

    t_end = time.time() + timeout
    running = True
    job_task_handler = job_manager_api.JobsTasksManager(
        config.JOB_MANAGER_URL
    )  # deal with job task api's
    find_job_params = {
        "resourceId": product_id,
        "version": product_version,
        # example to make it compatible to query params
        "shouldReturnTasks": str(True).lower(),
        "type": "Discrete-Tiling",
    }
    resp = job_task_handler.find_jobs_by_criteria(find_job_params)[0]
    if not resp:
        raise RuntimeError(f"Job for {product_id}:{product_version} not found")
    _log.info(
        f"Found job with details:\n"
        f'id: [{resp["id"]}]\n'
        f'resourceId (product id): [{resp["resourceId"]}]\n'
        f'version: [{resp["version"]}]\n'
        f'parameters: [{resp["parameters"]}]\n'
        f'status: [{resp["status"]}]\n'
        f'percentage: [{resp["percentage"]}]\n'
        f'reason: [{resp["reason"]}]\n'
        f'isCleaned: [{resp["isCleaned"]}]\n'
        f'priority: [{resp["priority"]}]\n'
        f'Num of tasks related to job: [{len(resp["tasks"])}]'
    )
    job = resp

    while running:
        time.sleep(config.SYSTEM_DELAY // 4)
        job_id = job["id"]
        # now getting job info by unique job id
        job = job_task_handler.get_job_by_id(job_id)

        job_id = job["id"]

        status = job["status"]
        reason = job["reason"]
        tasks = job["tasks"]

        completed_task = sum(
            1 for task in tasks if task["status"] == config.JobStatus.Completed.name
        )
        _log.info(
            f"\nIngestion status of job for resource: {product_id}:{product_version} is [{status}]\n"
            f"finished tasks for current job: {completed_task} / {len(tasks)}"
        )

        if status == config.JobStatus.Completed.name:
            return {
                "status": status,
                "message": " ".join(["OK", reason]),
                "job_id": job_id,
            }
        elif status == config.JobStatus.Failed.name:
            return {
                "status": status,
                "message": " ".join([FAILED_, reason]),
                "job_id": job_id,
            }

        current_time = time.time()

        if t_end < current_time:
            return {
                "status": status,
                "message": " ".join(
                    [FAILED_, "got timeout while following job running"]
                ),
                "job_id": job_id,
            }


def follow_parallel_running_tasks(
        product_id, product_version, timeout=config.FOLLOW_TIMEOUT
):
    """This method will follow running ingestion task and return results on finish"""

    t_end = time.time() + timeout
    running = True
    job_task_handler = job_manager_api.JobsTasksManager(
        config.JOB_MANAGER_URL
    )  # deal with job task api's
    find_job_params = {
        "resourceId": product_id,
        "version": product_version,
        # example to make it compatible to query params
        "shouldReturnTasks": str(True).lower(),
        "type": "Discrete-Tiling",
    }
    resp = job_task_handler.find_jobs_by_criteria(find_job_params)[0]
    received_tasks = job_task_handler.tasks(resp["id"])
    task_counter = 0
    for task_k in received_tasks:
        if task_k["status"] == "In-Progress":
            task_counter += 1

    if not resp:
        raise RuntimeError(f"Job for {product_id}:{product_version} not found")
    _log.info(
        f"Found job with details:\n"
        f'id: [{resp["id"]}]\n'
        f'resourceId (product id): [{resp["resourceId"]}]\n'
        f'version: [{resp["version"]}]\n'
        f'parameters: [{resp["parameters"]}]\n'
        f'status: [{resp["status"]}]\n'
        f'percentage: [{resp["percentage"]}]\n'
        f'reason: [{resp["reason"]}]\n'
        f'isCleaned: [{resp["isCleaned"]}]\n'
        f'priority: [{resp["priority"]}]\n'
        f'Num of tasks related to job: [{len(resp["tasks"])}]'
    )
    job = resp

    job_id = resp["id"]

    while running:
        time.sleep(config.SYSTEM_DELAY // 4)
        job_id = job["id"]
        # now getting job info by unique job id
        job = job_task_handler.get_job_by_id(job_id)

        job_id = job["id"]

        status = job["status"]
        reason = job["reason"]
        tasks = job["tasks"]

        completed_task = sum(
            1 for task in tasks if task["status"] == config.JobStatus.Completed.name
        )
        _log.info(
            f"\nIngestion status of job for resource: {product_id}:{product_version} is [{status}]\n"
            f"finished tasks for current job: {completed_task} / {len(tasks)}"
        )

        if status == config.JobStatus.Completed.name:
            return {
                "status": status,
                "message": " ".join(["OK", reason]),
                "job_id": job_id,
                "in_progress_tasks": task_counter,
            }
        elif status == config.JobStatus.Failed.name:
            return {
                "status": status,
                "message": " ".join([FAILED_, reason]),
                "job_id": job_id,
                "in_progress_tasks": task_counter,
            }

        current_time = time.time()

        if t_end < current_time:
            return {
                "status": status,
                "message": " ".join(
                    [FAILED_, "got timeout while following job running"]
                ),
                "job_id": job_id,
            }
    #
    # while running:
    #     time.sleep(config.SYSTEM_DELAY // 4)
    #     job_id = job['id']
    #     job = job_task_handler.get_job_by_id(job_id)  # now getting job info by unique job id
    #
    #     job_id = job['id']
    #
    #     status = job['status']
    #     reason = job['reason']
    #     tasks = job['tasks']
    #
    #     completed_task = sum(1 for task in tasks if task['status'] == config.JobStatus.Completed.name)
    #     _log.info(f'\nIngestion status of job for resource: {product_id}:{product_version} is [{status}]\n'
    #               f'finished tasks for current job: {completed_task} / {len(tasks)}')
    #
    #     if status == config.JobStatus.Completed.name:
    #         return {'status': status, 'message': " ".join(['OK', reason]), 'job_id': job_id}
    #     elif status == config.JobStatus.Failed.name:
    #         return {'status': status, 'message': " ".join(['Failed: ', reason]), 'job_id': job_id}
    #
    #     current_time = time.time()
    #
    #     if t_end < current_time:
    #         return {'status': status, 'message': " ".join(['Failed: ', 'got timeout while following job running']),
    #                 'job_id': job_id}


def update_shape_fs(shp):
    current_time_str = (
        common.generate_datatime_zulu().replace("-", "_").replace(":", "_")
    )
    resp = shape_convertor.add_ext_source_name(shp, current_time_str)
    return resp


def update_shape_fs_to_failure(shp):
    resp = shape_convertor.add_ext_source_name(shp, "duplication")
    return resp


def validate_tiff_exists(path_name, tiff_list):
    err = ""
    x = {}
    text_files = glob.glob(path_name + "/**/*.tif", recursive=True)
    for item in tiff_list:
        if "." in item:
            item = item.split(".")[0]
        if any(item in text for text in text_files):
            x[item] = True
        else:
            x[item] = False
            err = "tiff files missing :" + item
    if len(text_files) != len(tiff_list):
        x["length_is_equal"] = False
        err = "tiff files length is not equal"
    else:
        x["length_is_equal"] = True
    if err:
        return x, err
    else:
        return x, ""


def cleanup_env(product_id, product_version, initial_mapproxy_config):
    try:
        """This method will clean all created test data"""
        job_id = postgress_adapter.get_current_job_id(product_id, product_version)
        postgress_adapter.clean_job_task(job_id)
        # postgress_adapter.clean_layer_history(product_id)
        # postgress_adapter.clean_pycsw_record(product_id)
        if (
                config.TEST_ENV == config.EnvironmentTypes.QA.name
                or config.TEST_ENV == config.EnvironmentTypes.DEV.name
        ):
            s3_conn = s3.S3Client(
                config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY
            )
            s3_conn.delete_folder(config.S3_BUCKET_NAME, product_id)
        elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
            path = os.path.join(config.NFS_TILES_DIR, product_id, product_version)

            try:
                if os.path.exists(path):
                    # ToDo : Fix it
                    print("Starting Delete")
                    # if config.DELETE_INGESTION_FOLDER:
                    #     command = f"rm -rf {path}"
                    #     os.system(command)
                else:
                    # todo maybe on future add it with exception and test step
                    # assertion
                    _log.error(f"Directory of tiles [{path}] not exists on File System")

            except Exception as e:
                _log.error(
                    f"Failed deleting from File System the dir: [{str(path)}] with error: [{str(e)}]"
                )

        else:
            raise ValueError(
                f'Wrong \\ not given "TEST_ENV" configuration: [{config.TEST_ENV}]'
            )
        current_config_mapproxy = postgress_adapter.get_mapproxy_configs(
            table_name="config", db_name=config.PG_MAPPROXY_CONFIG
        )
        postgress_adapter.clean_pycsw_record(product_id)
        if len(current_config_mapproxy) > len(initial_mapproxy_config):
            if current_config_mapproxy[0]["id"] != "1":
                postgress_adapter.delete_config_mapproxy(
                    "id", current_config_mapproxy[0]["id"]
                )
            if current_config_mapproxy[1]["id"] != "1":
                postgress_adapter.delete_config_mapproxy(
                    "id", current_config_mapproxy[1]["id"]
                )
        postgress_adapter.delete_agent_path("layerId", product_id)
        postgress_adapter.delete_pycsw_record("product_id", product_id)

        _log.info(
            f"Cleanup was executed and delete at end of test:\n"
            f"DB - job and related task\n"
            f"DB - mapproxy-config\n"
            f"DB - pycsw-records\n"
            f"DB - agent-discrete\n"
            f"S3 - uploaded layers\n"
        )

    except Exception as e:
        _log.error(f"Failed on cleanup with error: {str(e)}")


def validate_geopack_pycsw(source_json_metadata, product_id=None, product_version=None):
    res_dict = {"validation": True, "reason": ""}
    pycsw_records = pycsw_handler.get_record_by_id(
        product_id,
        product_version,
        host=config.PYCSW_URL,
        params=config.PYCSW_GET_RECORD_PARAMS,
    )
    if not pycsw_records:
        return {"validation": False, "reason": f"Records of [{product_id}] not found"}
    links = {}
    for record in pycsw_records:
        links[record["mc:productType"]] = {
            record["mc:links"][0]["@scheme"]: record["mc:links"][0]["#text"],
            record["mc:links"][1]["@scheme"]: record["mc:links"][1]["#text"],
            record["mc:links"][2]["@scheme"]: record["mc:links"][2]["#text"],
        }
    if config.TEST_ENV == "PROD":
        source_json_metadata_dic = {"metadata": source_json_metadata}
        validation_flag, err_dict = validate_pycsw_with_shape_json(
            pycsw_records, source_json_metadata_dic
        )
    else:
        validation_flag, err_dict = validate_pycsw_with_shape_json(
            pycsw_records, source_json_metadata
        )
    res_dict["validation"] = validation_flag
    res_dict["reason"] = err_dict
    return res_dict, pycsw_records, links


def validate_pycsw2(source_json_metadata, product_id=None, product_version=None):
    """
    :return: dict of result validation
    """
    res_dict = {"validation": True, "reason": ""}
    try:
        pycsw_conn = pycsw_validator.PycswHandler(config.PYCSW_URL, config.PYCSW_GET_RECORD_PARAMS)
        results = pycsw_conn.validate_pycsw(source_json_metadata, product_id, product_version)
        res_dict = results['results']
        pycsw_records = results['pycsw_record']
        links = results['links']
        _log.info(f'')

    except Exception as e:
        _log.error(f'Failed validation of pycsw with error: [{str(e)}]')
        res_dict = {'validation': False, 'reason': str(e)}
        pycsw_records = {}
        links = {}

    _log.info(
        f'\n-------------------------- Finish validation of toc metadata vs. pycsw record ----------------------------')
    # pycsw_records = pycsw_handler.get_record_by_id(
    #     product_id,
    #     product_version,
    #     host=config.PYCSW_URL,
    #     params=config.PYCSW_GET_RECORD_PARAMS,
    # )

    # if not pycsw_records:
    #     return {"validation": False, "reason": f"Records of [{product_id}] not found"}
    # links = {}
    # for record in pycsw_records:
    #     links[record["mc:productType"]] = {
    #         record["mc:links"][0]["@scheme"]: record["mc:links"][0]["#text"],
    #         record["mc:links"][1]["@scheme"]: record["mc:links"][1]["#text"],
    #         record["mc:links"][2]["@scheme"]: record["mc:links"][2]["#text"],
    #     }
    # if config.TEST_ENV == "PROD":
    #     source_json_metadata_dic = {"metadata": source_json_metadata}
    #     validation_flag, err_dict = validate_pycsw_with_shape_json(
    #         pycsw_records, source_json_metadata_dic
    #     )
    # else:
    #     validation_flag, err_dict = validate_pycsw_with_shape_json(
    #         pycsw_records, source_json_metadata
    #     )
    # res_dict["validation"] = validation_flag
    # res_dict["reason"] = err_dict
    return res_dict, pycsw_records, links


def validate_pycsw(gqk=config.GQK_URL, product_id=None, source_data=None):
    """
    :return: dict of result validation
    """
    pycsw_record = pycsw_handler.get_record_by_id(
        source_data,
        product_id,
        host=config.PYCSW_URL,
        params=config.PYCSW_GET_RECORD_PARAMS,
    )

    res_dict = {"validation": True, "reason": ""}
    # pycsw_record = gql_wrapper.get_pycsw_record(host=gqk, product_id=product_id)
    if not pycsw_record["data"]["search"]:
        return {"validation": False, "reason": f"Record of [{product_id}] not found"}

    # generate dict of protocol:related url
    links = {
        pycsw_record["data"]["search"][0]["links"][0]["protocol"]: pycsw_record["data"][
            "search"
        ][0]["links"][0]["url"],
        pycsw_record["data"]["search"][0]["links"][1]["protocol"]: pycsw_record["data"][
            "search"
        ][0]["links"][1]["url"],
        pycsw_record["data"]["search"][0]["links"][2]["protocol"]: pycsw_record["data"][
            "search"
        ][0]["links"][2]["url"],
    }

    WMS_STATE = (
            base_requests.send_get_request(links["WMS"]).status_code
            == config.ResponseCode.Ok.value
    )
    WMTS_STATE = (
            base_requests.send_get_request(links["WMTS"]).status_code
            == config.ResponseCode.Ok.value
    )

    if not WMS_STATE and not WMTS_STATE:
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [res_dict["reason"], f"\nProtocol urls that provided not correct: {links}"]
        )

    # validate product id:
    record_product_id = pycsw_record["data"]["search"][0]["productId"]
    orig_product_id = source_data["metadata"]["productId"]
    if record_product_id != orig_product_id:
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [
                res_dict["reason"],
                f"\nWrong product id: orig:[{orig_product_id}] != pycsw_record:[{record_product_id}]",
            ]
        )

    # validate product name:
    record_product_name = pycsw_record["data"]["search"][0]["productName"]
    orig_product_name = source_data["metadata"]["productName"]
    if record_product_name != orig_product_name:
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [
                res_dict["reason"],
                f"\nWrong product name: orig name:[{orig_product_name}] != pycsw_record name:[{record_product_name}]",
            ]
        )

    # validate description:
    record_description = pycsw_record["data"]["search"][0]["description"]
    orig_description = source_data["metadata"]["description"]
    if record_description != orig_description:
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [
                res_dict["reason"],
                f"\nWrong description: orig description:[{orig_description}] != pycsw_record description:[{record_description}]",
            ]
        )

    # validate sensor type:
    record_sensor = pycsw_record["data"]["search"][0]["sensorType"]
    orig_sensor = source_data["metadata"]["sensorType"]
    if orig_sensor != record_sensor:
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [
                res_dict["reason"],
                f"\nWrong sensor types: orig sensor types:[{orig_sensor}] != pycsw_record sensor types:[{record_sensor}]",
            ]
        )

    # validate accuracy:
    record_accuracy = str(pycsw_record["data"]["search"][0]["accuracyCE90"])
    orig_accuracy = str(source_data["metadata"]["accuracyCE90"])
    if orig_accuracy != record_accuracy:
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [
                res_dict["reason"],
                f"\nWrong accuracy: orig accuracy:[{orig_accuracy}] != pycsw_record accuracy:[{record_accuracy}]",
            ]
        )

    # validate geometry:
    record_geometry = pycsw_record["data"]["search"][0]["footprint"]["coordinates"][0]
    orig_geometry = source_data["metadata"]["footprint"]["coordinates"][0]
    poly_record = Polygon(record_geometry)
    poly_orig = Polygon(orig_geometry)

    if not poly_record.equals(poly_orig):
        res_dict["validation"] = False
        res_dict["reason"] = "\n----------------------".join(
            [
                res_dict["reason"],
                f"\nWrong geometry: orig geometry:[{orig_geometry}] != pycsw_record geometry:[{record_geometry}]",
            ]
        )

    return res_dict, pycsw_record


def copy_geopackage_file_for_ingest():
    msg_text = None
    resp_status = None
    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        pvc_handler = azure_pvc_api.PVCHandler(
            endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
        )
        try:
            src_folder_to_copy = config.GEO_PACKAGE_SRC_PVC
            copied_dest_folder = config.GEO_PACKAGE_DEST_PVC
            resp = pvc_handler.copy_file_to_dest(src_folder=src_folder_to_copy, dest_folder=copied_dest_folder)
            msg_text = json.loads(resp.text)
            resp_status = resp.status_code
            source_folder = msg_text['source']
            new_destination = msg_text['newDesination']
            _log.info(msg_text['message'])
            _log.info(f'status code : {resp_status}')
            _log.info(f'source folder : {source_folder}')
            _log.info(f'new destination : {new_destination}')
        except Exception as e:
            resp = None
            error_msg = str(e)

    if config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        try:
            command = f"cp -r {config.GEO_PACKAGE_SRC_NFS}/. {config.GEO_PACKAGE_DEST_NFS}"
            os.system(command)
            if os.path.exists(config.GEO_PACKAGE_DEST_NFS):
                _log.info(f"Success copy and creation of test data on: {config.GEO_PACKAGE_DEST_NFS}")
            else:
                raise IOError("Failed on creating ingestion directory")
            resp_status = 201
            msg_text = {'source': config.GEO_PACKAGE_SRC_NFS}
        except Exception as e:
            resp_status = None
            msg_text = 'error'
            _log.error(
                f"Failed copy files from {config.GEO_PACKAGE_SRC_NFS} into {config.GEO_PACKAGE_DEST_NFS} with error: [{str(e)}]")
            raise e
    return resp_status, msg_text


def validate_mapproxy_layer(pycsw_record, product_id, product_version, params=None):
    """
    This method will ensure the url's provided on mapproxy from pycsw
    :return: result dict -> {'validation': bool, 'reason':{}}, links -> dict
    """
    _log.info(
        f'\n\n********************** Will run validation of layer mapproxy vs. pycsw record *************************')

    if params['tiles_storage_provide'].lower() == 's3':
        s3_credential = structs.S3Provider(entrypoint_url=params['endpoint_url'],
                                           access_key=params['access_key'],
                                           secret_key=params['secret_key'],
                                           bucket_name=params['bucket_name'])
    else:
        s3_credential = None
    mapproxy_conn = mapproxy_validator.MapproxyHandler(entrypoint_url=params['mapproxy_endpoint_url'],
                                                       tiles_storage_provide=params['tiles_storage_provide'],
                                                       grid_origin=params['grid_origin'],
                                                       s3_credential=s3_credential,
                                                       nfs_tiles_url=params['nfs_tiles_url'])

    res = mapproxy_conn.validate_layer_from_pycsw(pycsw_record, product_id, product_version)
    return res

    _log.info(
        f'\n----------------------- Finish validation of layer mapproxy vs. pycsw record ---------------------------')


def validate_new_discrete(pycsw_records, product_id, product_version):
    """
    This method will validate access and data on mapproxy
    :return:
    """
    if not pycsw_records:
        raise ValueError(f"input pycsw is empty: [{pycsw_records}]")
    links = {}
    for records in pycsw_records:
        links[records["mc:productType"]] = {
            link["@scheme"]: link["#text"] for link in records["mc:links"]
        }

    results = dict.fromkeys(list(links.keys()), dict())
    for link_group in list(links.keys()):
        results[link_group] = {k: v for k, v in links[link_group].items()}

    for group in results.keys():
        if group == "Orthophoto":
            layer_name = "-".join([product_id, group])
        elif group == "OrthophotoHistory":
            # layer name
            layer_name = "-".join([product_id, product_version, group])
        else:
            raise ValueError(
                f"records type on recognize as OrthophotoHistory or Orthophoto"
            )

        results[group]["is_valid"] = {}
        # check that wms include the new layer on capabilities
        wms_capabilities = common.get_xml_as_dict(results[group]["WMS"])
        results[group]["is_valid"]["WMS"] = layer_name in [
            layer["Name"]
            for layer in wms_capabilities["WMS_Capabilities"]["Capability"]["Layer"][
                "Layer"
            ]
        ]

        # check that wmts include the new layer on capabilities
        wmts_capabilities = common.get_xml_as_dict(results[group]["WMTS"])
        results[group]["is_valid"]["WMTS"] = layer_name in [
            layer["ows:Identifier"]
            for layer in wmts_capabilities["Capabilities"]["Contents"]["Layer"]
        ]
        wmts_layer_properties = [
            layer
            for layer in wmts_capabilities["Capabilities"]["Contents"]["Layer"]
            if layer_name in layer["ows:Identifier"]
        ]

        # check access to random tile by wmts_layer url
        if (
                config.TEST_ENV == config.EnvironmentTypes.QA.name
                or config.TEST_ENV == config.EnvironmentTypes.DEV.name
        ):
            s3_conn = s3.S3Client(
                config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY
            )
            list_of_tiles = s3_conn.list_folder_content(
                config.S3_BUCKET_NAME, "/".join([product_id, product_version])
            )
        elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
            path = os.path.join(config.NFS_TILES_DIR, product_id, product_version)
            list_of_tiles = []
            # r=root, d=directories, f = files
            for r, d, f in os.walk(path):
                for file in f:
                    if ".png" in file:
                        list_of_tiles.append(os.path.join(r, file))
        else:
            raise RuntimeError(f"Illegal environment value type: {config.TEST_ENV}")

        zxy = list_of_tiles[len(list_of_tiles) - 1].split("/")[-3:]
        zxy[2] = zxy[2].split(".")[0]
        zxy[2] = str(2 ** int(zxy[0]) - 1 - int(zxy[2]))
        tile_matrix_set = wmts_layer_properties[0]["TileMatrixSetLink"]["TileMatrixSet"]
        wmts_layers_url = results[group]["WMTS_LAYER"]
        wmts_layers_url = wmts_layers_url.format(
            TileMatrixSet=tile_matrix_set,
            TileMatrix=zxy[0],
            TileCol=zxy[1],
            TileRow=zxy[2],
        )  # formatted url for testing
        resp = base_requests.send_get_request(wmts_layers_url)
        results[group]["is_valid"]["WMTS_LAYER"] = (
                resp.status_code == config.ResponseCode.Ok.value
        )

    # validation iteration -> check if all URL's state is True
    validation = True
    for group_name, value in results.items():
        if not all(val for key, val in value["is_valid"].items()):
            validation = False
            break
    _log.info(f"validation of discrete layers on mapproxy status:\n" f"{results}")
    return {"validation": validation, "reason": results}


def get_json_schema(path_to_schema):
    """This function loads the given schema available"""
    try:
        with open(path_to_schema, "r") as file:
            schema = json.load(file)
    except IOError:
        return None
    return schema


def get_folder_path_by_name(path, name):
    p_walker = [x[0] for x in os.walk(path)]
    path = "\n".join(s for s in p_walker if name.lower() in s.lower())
    return path


def get_xml_as_dict(url):
    """
    This method request xml and return response as dict [ordered]
    """
    try:
        response = base_requests.send_get_request(url)
        dict_data = xmltodict.parse(response.content)
        return dict_data

    except Exception as e:
        _log.error(f"Failed getting xml object from url [{url}] with error: {str(e)}")
        raise RuntimeError(
            f"Failed getting xml object from url [{url}] with error: {str(e)}"
        )


def create_mock_file(path_to_folder, file_to_create):
    ret_folder = glob.glob(path_to_folder + "/**/" + file_to_create, recursive=True)
    if not ret_folder:
        raise RuntimeError(f"{file_to_create} not found in {path_to_folder}")
    try:
        for folder in ret_folder:
            os.remove(folder)
            Path(folder).touch()
    except OSError as e:
        raise RuntimeError(f"error occurred , msg : {str(e)}")


def write_text_to_file(path_to_text, text_to_write):
    if not path_to_text:
        path_to_text = "//tmp//jobs_to_delete.txt"
    try:
        with open(path_to_text, "a") as f:
            f.write(f"{text_to_write}\n")
    except IOError as e:
        raise RuntimeError(f"Failed to write to {path_to_text} , with msg : {str(e)}")
