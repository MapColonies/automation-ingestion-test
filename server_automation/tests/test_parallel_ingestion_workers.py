import logging
import os
import shutil
from time import sleep

from conftest_val import ValueStorage
from server_automation.configuration import config
from server_automation.functions.executors import azure_pvc_api
from server_automation.functions.executors import cleanup_env
from server_automation.functions.executors import follow_parallel_running_tasks
from server_automation.functions.executors import init_ingestion_src
from server_automation.functions.executors import postgress_adapter
from server_automation.functions.executors import start_manual_ingestion
from server_automation.functions.executors import stop_watch
from server_automation.functions.executors import update_shape_zoom_level
from server_automation.functions.executors import write_text_to_file

"""
  For 2 Workers:
  discreteOverseer.env.TILING_ZOOM_GROUPS
    0-5,6,7,8,9,10,11,12,13,14

    discreteWorker.replicaCount = 2

    zoom_level = 14
   "amount_of_workers": 2
    "system_delay": 250,
    "progress_task_delay": 10,
    "follow_timeout": 5

"""

_log = logging.getLogger("server_automation.tests.test_parallel_ingestion_workers")

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_parallel_ingestion():
    try:
        resp = init_ingestion_src()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_parallel_ingestion.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")

    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp["ingestion_dir"]
    _log.info(f"{product_id} {product_version}")
    ValueStorage.folder_to_delete = source_directory.split("/watch/")[-1]

    if config.WRITE_TEXT_TO_FILE:
        write_text_to_file(
            "//tmp//shlomo.txt",
            {
                "source_dir": source_directory,
                "product_id_version": ValueStorage.discrete_list,
                "test_name": test_parallel_ingestion.__name__,
                "folder_to_delete": ValueStorage.folder_to_delete,
            },
        )

    sleep(5)

    if config.SOURCE_DATA_PROVIDER.lower() == "pv":
        pvc_handler = azure_pvc_api.PVCHandler(
            endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
        )
        pvc_handler.change_max_zoom_tfw(12)
    # ================================================================================================================ #
    if config.SOURCE_DATA_PROVIDER.lower() == "nfs":
        resp_from_update = update_shape_zoom_level(
            source_directory, str(config.MAX_ZOOM_TO_CHANGE)
        )
        _log.info(f"Zoom update response: {str(resp_from_update)}")
    try:
        status_code, content, source_data = start_manual_ingestion(source_directory)
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_parallel_ingestion.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info(f"manual ingestion - source_data: {source_data}")
    _log.info(f"manual ingestion - content: {content}")
    _log.info(f"manual ingestion - status code: {status_code}")
    # ================================================================================================================ #

    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            sleep(config.PROGRESS_TASK_DELAY)
            ingestion_in_progress_state = follow_parallel_running_tasks(
                product_id, product_version
            )

    except Exception as e:
        resp = None
        error_msg = str(e)
    if error_msg is None:
        error_msg = "Workers not equal to progress tasks"
    num_tasks = ingestion_in_progress_state["in_progress_tasks"]
    resp = ingestion_in_progress_state["status"] == config.JobStatus.Completed.name
    error_msg = ingestion_in_progress_state["message"]

    assert (
        resp
    ), f"Test: [{test_parallel_ingestion.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"manual ingestion following task response: {resp}")

    assert (
        num_tasks == config.AMOUNT_OF_WORKERS
    ), f"Test: [{test_parallel_ingestion.__name__}] Failed: on following ingestion process [{error_msg} , actually {num_tasks} but expected : {config.AMOUNT_OF_WORKERS}]"
    _log.info(f"manual ingestion following task response: {resp}")
    _log.info(
        f"finished parallel test for : {config.AMOUNT_OF_WORKERS} workers (tasks number in parallel)"
    )
    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.SYSTEM_DELAY)


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """
    stop_watch()
    if config.CLEAN_UP:
        for p in ValueStorage.discrete_list:
            cleanup_env(p["product_id"], p["product_version"], initial_mapproxy_config)


if config.DEBUG_MODE_LOCAL:
    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 14  # 4
if config.RUN_IT:
    test_parallel_ingestion()
