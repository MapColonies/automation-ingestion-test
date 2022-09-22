"""This module provides multiple test of ingestion services"""
import json
import logging
import shutil
from time import sleep

from discrete_kit.functions.shape_functions import ShapeToJSON
from discrete_kit.validator.json_compare_pycsw import *
from mc_automation_tools.parse.stringy import pad_with_minus
from mc_automation_tools.parse.stringy import pad_with_stars

from conftest_val import ValueStorage
from server_automation.configuration import config
from server_automation.functions.executors import *
from server_automation.postgress import postgress_adapter

_log = logging.getLogger("server_automation.tests.test_ingestion_discrete")

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_manual_discrete_ingest():
    """
    This test will test full e2e discrete ingestion
    """
    _log.info("\n" + pad_with_minus("Started - Stop watch"))
    watch_resp = stop_watch()
    if watch_resp:
        _log.info(
            f"watch state = {watch_resp['state']}, watch response is : {watch_resp['reason']}"
        )
    _log.info("\n" + pad_with_minus("Finished - Stop watch"))

    folder_name, resource_new_name = init_ingestion_folder()

    product_id, product_version = resource_new_name.split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = folder_name
    _log.info(f"Product_id : {product_id} , Product_version : {product_version}")
    sleep(5)

    if config.WRITE_TEXT_TO_FILE:
        _log.info("\n" + pad_with_minus("Started - Write Tests to files"))
        write_text_to_file(
            "//tmp//test_runs.txt",
            {
                "source_dir": source_directory,
                "product_id_version": ValueStorage.discrete_list,
                "test_name": test_manual_discrete_ingest.__name__,
                "folder_to_delete": ValueStorage.folder_to_delete,
            },
        )
        _log.info("\n" + pad_with_minus("Finished - Write Tests to files"))

    _log.info("\n" + pad_with_minus("Started - manual ingestion"))
    try:
        status_code, content, source_data = start_manual_ingestion(source_directory)
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_manual_discrete_ingest.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info(f"manual ingestion - source_data: {source_data}")
    _log.info(f"manual ingestion - content: {content}")
    _log.info(f"manual ingestion - status code: {status_code}")
    _log.info("\n" + pad_with_minus("Finished - manual ingestion"))

    _log.info("\n" + pad_with_minus("Started - follow manual ingestion job"))
    # validating following and completion of ingestion job
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            ingestion_follow_state = follow_running_job_manager(
                product_id, product_version
            )
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(product_id, product_version)
        resp = ingestion_follow_state["status"] == config.JobStatus.Completed.name
        error_msg = ingestion_follow_state["message"]

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"manual ingestion following task response: {resp}")
    _log.info("\n" + pad_with_minus("Finished - follow manual ingestion job"))

    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.DELAY_INGESTION_TEST)
    pycsw_record = None

    _log.info("\n" + pad_with_minus("Started - validation of manual ingestion"))
    # validate new discrete on pycsw records
    try:
        resp, pycsw_record, links = validate_pycsw2(
            source_data, product_id, product_version
        )
        # todo this is legacy records validator based graphql -> for future needs maybe
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_manual_discrete_ingest.__name__}] Failed: validation of pycsw record\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        _log.info(f"manual ingestion validation - response: {resp}")
        _log.info(f"manual ingestion validation - pycsw_record: {pycsw_record}")
        _log.info(f"manual ingestion validation - links: {links}")

    sleep(config.DELAY_MAPPROXY_PYCSW_VALIDATION)
    # validating new discrete on mapproxy

    try:
        params = {
            "mapproxy_endpoint_url": config.MAPPROXY_URL,
            "tiles_storage_provide": config.TILES_PROVIDER,
            "grid_origin": config.MAPPROXY_GRID_ORIGIN,
            "nfs_tiles_url": config.NFS_TILES_DIR,
        }

        if config.TILES_PROVIDER.lower() == "s3":
            params["endpoint_url"] = config.S3_ENDPOINT_URL
            params["access_key"] = config.S3_ACCESS_KEY
            params["secret_key"] = config.S3_SECRET_KEY
            params["bucket_name"] = config.S3_BUCKET_NAME

        result = validate_mapproxy_layer(
            pycsw_record, product_id, product_version, params
        )
        mapproxy_validation_state = result["validation"]
        msg = result["reason"]

    except Exception as e:
        mapproxy_validation_state = False
        msg = str(e)

    assert mapproxy_validation_state, (
        f"Test: [{test_manual_discrete_ingest.__name__}] Failed: Validation of mapproxy urls\n"
        f"related errors:\n"
        f"{msg}"
    )
    if config.DEBUG_MODE_LOCAL:
        cleanup_env(product_id, product_version, initial_mapproxy_config)


def test_watch_discrete_ingest():
    """
    This test ingestion by watching shared folder
    """
    # sleep(300)
    try:
        resp = stop_watch()
        state = resp["state"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)
    assert (
        state
    ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on stop agent watch [{error_msg}]"
    _log.info(f"watch ingestion - stop watch response: {resp}")

    try:
        resp = init_watch_ingestion_src()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")
    # triggering and validate start of new manuel job
    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp["ingestion_dir"]
    ValueStorage.folder_to_delete = source_directory.split("/watch/")[-1]
    _log.info(f"{product_id} {product_version}")
    _log.info(f"watch ingestion init - source_directory: {source_directory}")
    write_text_to_file(
        "//tmp//shlomo.txt",
        {
            "source_dir": source_directory,
            "product_id_version": ValueStorage.discrete_list,
            "test_name": test_watch_discrete_ingest.__name__,
            "folder_to_delete": ValueStorage.folder_to_delete,
        },
    )
    try:
        state, content, source_data = start_watch_ingestion(source_directory)
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert state, (
        f"Test: [{test_watch_discrete_ingest.__name__}] Failed: Trigger ingest process from watch agent: [{status_code}]\n"
        f"details: [{content}]"
    )

    _log.info(f"watch ingestion ,start watch - state: {state}")
    _log.info(f"watch ingestion ,start watch - content: {content}")
    _log.info(f"watch ingestion ,start watch - source_data: {source_data}")

    sleep(config.DELAY_INGESTION_TEST)  # validate generation of new job
    # validating following and completion of ingestion job
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            ingestion_follow_state = follow_running_job_manager(
                product_id, product_version
            )
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(product_id, product_version)
            _log.info("Start following job-tasks based on bff api")
        resp = ingestion_follow_state["status"] == config.JobStatus.Completed.name
        error_msg = ingestion_follow_state["message"]

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"watch ingestion following task response:{resp}")

    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.DELAY_INGESTION_TEST * 2)
    pycsw_record = None
    try:
        resp, pycsw_record, links = validate_pycsw2(
            source_data, product_id, product_version
        )
        # todo this is legacy records validator based graphql -> for future needs maybe
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of pycsw record\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        _log.info(f"manual ingestion validation - response: {resp}")
        _log.info(f"manual ingestion validation - pycsw_record: {pycsw_record}")
        _log.info(f"manual ingestion validation - links: {links}")

    sleep(config.DELAY_MAPPROXY_PYCSW_VALIDATION)
    # validating new discrete on mapproxy

    try:
        params = {
            "mapproxy_endpoint_url": config.MAPPROXY_URL,
            "tiles_storage_provide": config.TILES_PROVIDER,
            "grid_origin": config.MAPPROXY_GRID_ORIGIN,
            "nfs_tiles_url": config.NFS_TILES_DIR,
        }

        if config.TILES_PROVIDER.lower() == "s3":
            params["endpoint_url"] = config.S3_ENDPOINT_URL
            params["access_key"] = config.S3_ACCESS_KEY
            params["secret_key"] = config.S3_SECRET_KEY
            params["bucket_name"] = config.S3_BUCKET_NAME

        result = validate_mapproxy_layer(
            pycsw_record, product_id, product_version, params
        )
        mapproxy_validation_state = result["validation"]
        msg = result["reason"]

    except Exception as e:
        mapproxy_validation_state = False
        msg = str(e)

    assert mapproxy_validation_state, (
        f"Test: [{test_watch_discrete_ingest.__name__}] Failed: Validation of mapproxy urls\n"
        f"related errors:\n"
        f"{msg}"
    )

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of mapproxy layer\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        resp = stop_watch()
        _log.info(
            f'watch ingestion, Finish running watch ingestion. Watch status: [{resp["reason"]}]'
        )


def init_ingestion_folder():
    if config.SOURCE_DATA_PROVIDER.lower() == "pv":
        return pv_init_ingestion_flow()
    if config.SOURCE_DATA_PROVIDER.lower() == "nfs":
        return nfs_init_ingestion_flow()
    else:
        raise ValueError(
            f"Illegal environment value type: {config.SOURCE_DATA_PROVIDER.lower()}"
        )


def nfs_init_ingestion_flow():
    src = os.path.join(config.NFS_ROOT_DIR, config.NFS_SOURCE_DIR)
    dst = os.path.join(config.NFS_ROOT_DIR_DEST, config.NFS_DEST_DIR)
    try:
        res = init_ingest_nfs(
            src, dst, str(config.zoom_level_dict[config.MAX_ZOOM_TO_CHANGE])
        )
        # res = init_ingestion_src_fs(src, dst, str(config.zoom_level_dict[config.MAX_ZOOM_TO_CHANGE]), watch=False)
        return res
    except FileNotFoundError as e:
        raise e
    except Exception as e1:
        raise RuntimeError(f"Failed generating testing directory with error: {str(e1)}")


def pv_init_ingestion_flow():
    _log.info("\n" + pad_with_stars("Started - create ingestion folder"))
    try:
        destination_folder, resp_code = create_ingestion_folder_pvc(False)
    except RuntimeError as err:
        create_folder_err = str(err)

    assert (
        resp_code.status_code == config.ResponseCode.ChangeOk.value
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: create folder with status code: [{resp_code.status_code}],details : [{create_folder_err}]"
    _log.info("\n" + pad_with_stars("Finished - create ingestion folder"))

    _log.info("\n" + pad_with_stars("Started - update ingestion source name"))
    try:
        updated_source_name, resp_code = update_ingestion_folder_pvc(False)
    except Exception as err:
        update_source_name_err = str(err)

    assert (
        resp_code.status_code == config.ResponseCode.ChangeOk.value
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: update source name with status code: [{resp_code.status_code}],details : [{update_source_name_err}] "
    _log.info("\n" + pad_with_stars("Finished - update ingestion source name"))

    _log.info("\n" + pad_with_stars("Started - change zoom level"))
    try:
        resp_code = change_zoom_level_pvc(config.MAX_ZOOM_TO_CHANGE)
    except Exception as err:
        change_zoom_err = str(err)
    assert (
        resp_code.status_code == config.ResponseCode.Ok.value
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: change zoom with status code: [{resp_code.status_code}],details : [{change_zoom_err}] "
    _log.info("\n" + pad_with_stars("Finished - change zoom level"))
    return destination_folder, updated_source_name


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """
    stop_watch()
    if config.CLEAN_UP:
        for p in ValueStorage.discrete_list:
            cleanup_env(p["product_id"], p["product_version"], initial_mapproxy_config)


test_manual_discrete_ingest()
# test_watch_discrete_ingest()
