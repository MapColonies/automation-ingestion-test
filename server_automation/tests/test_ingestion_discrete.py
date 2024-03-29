"""This module provides multiple test of ingestion services"""
import logging
from time import sleep

from mc_automation_tools.parse.stringy import pad_with_minus
from mc_automation_tools.parse.stringy import pad_with_stars

from conftest_val import ValueStorage
from server_automation.configuration import config
from server_automation.functions.executors import cleanup_env
from server_automation.functions.executors import follow_running_job_manager
from server_automation.functions.executors import follow_running_task
from server_automation.functions.executors import init_ingestion_src
from server_automation.functions.executors import init_watch_ingestion_src
from server_automation.functions.executors import start_manual_ingestion
from server_automation.functions.executors import start_watch_ingestion
from server_automation.functions.executors import stop_watch
from server_automation.functions.executors import validate_mapproxy_layer
from server_automation.functions.executors import validate_pycsw2
from server_automation.functions.executors import write_text_to_file
from server_automation.postgress import postgress_adapter

# from discrete_kit.functions.shape_functions import ShapeToJSON
# from discrete_kit.validator.json_compare_pycsw import *

_log = logging.getLogger("server_automation.tests.test_ingestion_discrete")


if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_manual_discrete_ingest():
    """
    This test will test full e2e discrete ingestion
    """
    _log.propagate = False
    watch_resp = stop_watch()
    if watch_resp:
        _log.info(
            f"watch state = {watch_resp['state']}, watch response is : {watch_resp['reason']}"
        )

    resp_from_init_folder = init_ingestion_folder()

    product_id, product_version = resp_from_init_folder["resource_name"].split(
        "-"
    )
    # layer_id = ""
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp_from_init_folder["ingestion_dir"]
    _log.info(
        f"Product_id : {product_id} , Product_version : {product_version}"
    )
    sleep(5)

    if config.WRITE_TEXT_TO_FILE:
        _log.info("Starting - Write Tests to files.................")
        write_text_to_file(
            "//tmp//test_runs.txt",
            {
                "source_dir": source_directory,
                "product_id_version": ValueStorage.discrete_list,
                "test_name": test_manual_discrete_ingest.__name__,
                "folder_to_delete": ValueStorage.folder_to_delete,
            },
        )
        _log.info("Finished - Write Tests to files.................")

    _log.info("Starting - manual ingestion...............")
    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory
        )

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

    # validating following and completion of ingestion job
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            ingestion_follow_state = follow_running_job_manager(
                product_id, product_version
            )
            layer_id = ingestion_follow_state['relative_path']
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(
                product_id, product_version
            )
        resp = (
            ingestion_follow_state["status"] == config.JobStatus.Completed.name
        )
        error_msg = ingestion_follow_state["message"]

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"manual ingestion following task response: {resp}")

    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.DELAY_INGESTION_TEST) # ToDo: Was 220 now 80
    pycsw_record = None

    # validate new discrete on pycsw records
    try:
        resp, pycsw_record, links = validate_pycsw2(
            source_data, product_id, product_version, token=config.TOKEN
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
        _log.info(
            f"manual ingestion validation - pycsw_record: {pycsw_record}"
        )
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
        # sleep(100)

        result = validate_mapproxy_layer(
            pycsw_record,
            product_id,
            product_version,
            layer_id=layer_id,
            params=params,
            token=config.TOKEN
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
            layer_id = ingestion_follow_state['relative_path']
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(
                product_id, product_version
            )
            _log.info("Start following job-tasks based on bff api")
        resp = (
            ingestion_follow_state["status"] == config.JobStatus.Completed.name
        )
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
        _log.info(
            f"manual ingestion validation - pycsw_record: {pycsw_record}"
        )
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
            pycsw_record,
            product_id,
            product_version,
            header=config.HEADERS_FOR_MAPPROXY,
            params=params,
            layer_id=layer_id,
            token=config.TOKEN
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

    # validate new discrete on pycsw records
    # try:
    #
    #     resp, pycsw_record, links = validate_pycsw2(
    #         source_data, product_id, product_version
    #     )
    #     # todo this is legacy records validator based graphql -> for future needs maybe
    #     # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
    #     state = resp["validation"]
    #     error_msg = resp["reason"]
    # except Exception as e:
    #     state = False
    #     error_msg = str(e)
    #
    # if config.VALIDATION_SWITCH:
    #     assert state, (
    #         f"Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of pycsw record\n"
    #         f"related errors:\n"
    #         f"{error_msg}"
    #     )
    #     _log.info(f"watch ingestion ,watch validation - response: {resp}")
    #     _log.info(f"watch ingestion ,watch validation - pycsw_record: {pycsw_record}")
    #     _log.info(f"watch ingestion ,watch validation - links: {links}")
    #
    # # validating new discrete on mapproxy
    # try:
    #     resp = validate_new_discrete(pycsw_record, product_id, product_version)
    #     state = resp["validation"]
    #     error_msg = resp["reason"]
    # except Exception as e:
    #     state = False
    #     error_msg = str(e)

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
    _log.info("\n" + pad_with_stars("Started - init_ingestion_folder"))
    try:
        resp = init_ingestion_src()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"Response [init_ingestion_src] : {resp}")
    _log.info(pad_with_minus("\nFinished - init_ingestion_folder"))
    return resp


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """
    stop_watch()
    if config.CLEAN_UP:
        for p in ValueStorage.discrete_list:
            cleanup_env(
                p["product_id"], p["product_version"], initial_mapproxy_config
            )


if config.DEBUG_MODE_LOCAL:
    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 4

if config.RUN_IT:
    test_manual_discrete_ingest()
    test_watch_discrete_ingest()
