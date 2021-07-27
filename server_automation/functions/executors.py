# pylint: disable=line-too-long, invalid-name, fixme
"""This module provide test full functionality """
import logging
import time
import json
import os
import subprocess
from server_automation.configuration import config
from server_automation.ingestion_api import discrete_agent_api, discrete_directory_loader, azure_pvc_api
from server_automation.postgress import postgress_adapter

from mc_automation_tools import common as common
from mc_automation_tools import shape_convertor
from mc_automation_tools import s3storage as s3

_log = logging.getLogger('server_automation.function.executors')


def init_ingestion_src(env=config.EnvironmentTypes.QA.name):
    """
    This module will init new ingestion source folder.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
        res = init_ingestion_src_pvc()
        return res
    elif env == config.EnvironmentTypes.PROD.name:
        src = os.path.join(config.NFS_ROOT_DIR, config.NFS_SOURCE_DIR)
        dst = os.path.join(config.NFS_ROOT_DIR, config.NFS_DEST_DIR)
        res = init_ingestion_src_fs(src, dst)
        return res
    else:
        raise Exception(f'Illegal environment value type: {env}')


def init_ingestion_src_fs(src, dst):
    """
        This module will init new ingestion source folder - for file system / NFS deployment.
        The prerequisites must have source folder with suitable data and destination folder for new data
        The method will duplicate and rename metadata shape file to unique running name
        :return:dict with ingestion_dir and resource_name
    """
    if os.path.exists(dst):
        command = f'rm -rf {dst}'
        os.system(command)

    if not os.path.exists(src):
        raise FileNotFoundError(f'[{src}] directory not found')

    try:
        command = f'cp -r {src}/. {dst}'
        os.system(command)
        _log.info(f'Success copy and creation of test data on: {dst}')

    except Exception as e2:
        _log.error(f'Failed copy files from {src} into {dst} with error: [{str(e2)}]')
        raise e2

    try:
        file = os.path.join(dst, config.SHAPES_PATH, config.SHAPE_METADATA_FILE)
        source_name = update_shape_fs(file)
        _log.info(
            f'[{file}]:was changed resource name: {source_name}')
    except Exception as e:
        _log.error(f'Failed on updating shape file: {file} with error: {str(e)}')
        raise e
    return {'ingestion_dir': dst, 'resource_name': source_name}


def init_ingestion_src_pvc():
    """
    This module will init new ingestion source folder inside pvc - only on azure.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    try:
        resp = azure_pvc_api.create_new_ingestion_dir(host=config.PVC_HANDLER_ROUTE, api=config.PVC_CLONE_SOURCE)
        if not resp.status_code == config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'Failed access pvc on source data cloning with error: [{resp.text}] and status: [{resp.status_code}]')
        msg = json.loads(resp.text)
        new_dir = msg['newDesination']
        _log.info(
            f'[{resp.status_code}]: New test running directory was created from source data: {msg["source"]} into {msg["newDesination"]}')
    except Exception as e:
        raise Exception(f'Failed access pvc on source data cloning with error: [{str(e)}]')

    try:
        resp = azure_pvc_api.make_unique_shapedata(host=config.PVC_HANDLER_ROUTE, api=config.PVC_CHANGE_METADATA)
        if not resp.status_code == config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'Failed access pvc on source data updating metadata.shp with error: [{resp.text}] and status: [{resp.status_code}]')
        resource_name = json.loads(resp.text)['source']
        _log.info(
            f'[{resp.status_code}]: metadata.shp was changed resource name: {resource_name}')

    except Exception as e:
        raise Exception(f'Failed access pvc on changing shape metadata: [{str(e)}]')

    return {'ingestion_dir': new_dir, 'resource_name': resource_name}


def validate_source_directory(path=None, env=config.EnvironmentTypes.QA.name):
    """
    This will validate that source directory include all needed files for ingestion
    :param path: None if working on azure - qa \ dev with pvc
    :param env: default qa for azure running with pvc
    :return: True \ False + response json
    """

    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
        resp = azure_pvc_api.validate_ingestion_directory()
        content = json.loads(resp.text)

        return not content['failure'], content['json_data']

    elif env == config.EnvironmentTypes.PROD.name:
        resp = discrete_directory_loader.validate_source_directory(path)
        return resp[0], resp[1]
    else:
        raise Exception(f'illegal Environment name: [{env}]')


def start_manuel_ingestion(path, env=config.EnvironmentTypes.QA.name):
    """This method will trigger new process of discrete ingestion by provided path"""
    # validate directory include all needed files and data
    source_ok, body = validate_source_directory(path, env)
    if not source_ok:
        raise FileNotFoundError(f'Directory [{path}] with missing files \ errors msg: [{body}]')


    _log.info(f'Send ingestion request for dir: {path}')
    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
       relative_path = path.split(config.PVC_ROOT_DIR)[1]
    elif env == config.EnvironmentTypes.PROD.name:
        relative_path = config.NFS_DEST_DIR

    resp = discrete_agent_api.post_manual_trigger(relative_path)
    status_code = resp.status_code
    content = resp.text
    _log.info(f'receive from agent - manual: status code [{status_code}] and message: [{content}]')
    return status_code, content


def follow_running_task(job_id, timeout=config.FOLLOW_TIMEOUT):
    """This method will follow running ingestion task and return results on finish"""

    t_end = time.time() + timeout
    running = True
    while running:
        job = postgress_adapter.get_job_by_id(job_id, db_name=config.PG_JOB_TASK_DB_NAME)
        status = job['status']
        if status == config.JobStatus.Completed.value:

            return {'status': status, 'message': 'OK'}
        else:
            print('temp = on progress')


def update_shape_fs(shp):
    current_time_str = common.generate_datatime_zulu().replace('-', '_').replace(':', '_')
    resp = shape_convertor.add_ext_source_name(shp, current_time_str)
    return resp
