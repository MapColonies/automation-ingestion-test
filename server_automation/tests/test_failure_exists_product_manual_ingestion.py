import logging
import os
from server_automation.configuration import config
from server_automation.functions.executors import postgress_adapter, init_ingestion_src, start_manual_ingestion, \
    write_text_to_file, follow_running_task, follow_running_job_manager, azure_pvc_api, stop_watch, cleanup_env
from conftest import ValueStorage
from time import sleep
import shutil

_log = logging.getLogger("server_automation.tests.test_ingestion_discrete")

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_exists_product_manual_ingestion():
    try:
        resp = init_ingestion_src()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_exists_product_manual_ingestion.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")

    # triggering and validate start of new manuel job
    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp["ingestion_dir"]
    ValueStorage.folder_to_delete = source_directory.split("/watch/")[-1]
    if config.WRITE_TEXT_TO_FILE:
        write_text_to_file('//tmp//shlomo.txt',
                           {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                            'test_name': test_exists_product_manual_ingestion.__name__,
                            'folder_to_delete': ValueStorage.folder_to_delete})
    _log.info(f"{product_id} {product_version}")
    sleep(5)
    # ================================================================================================================ #
    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory
        )
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_exists_product_manual_ingestion.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info(f"manual ingestion - source_data: {source_data}")
    _log.info(f"manual ingestion - content: {content}")
    _log.info(f"manual ingestion - status code: {status_code}")

    # ================================================================================================================ #
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
    ), f"Test: [{test_exists_product_manual_ingestion.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"manual ingestion following task response: {resp}")

    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.DELAY_INGESTION_TEST)

    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory
        )
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.DuplicatedError.value, (
        f"Test: [{test_exists_product_manual_ingestion.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info(f"manual ingestion - source_data: {source_data}")
    _log.info(f"manual ingestion - content: {content}")
    _log.info(f"manual ingestion - status code: {status_code}")


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """
    stop_watch()
    error_msg = ""
    pvc_handler = azure_pvc_api.PVCHandler(
        endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
    )
    if config.VALIDATION_SWITCH:
        if (
                config.TEST_ENV == config.EnvironmentTypes.QA.name
                or config.TEST_ENV == config.EnvironmentTypes.DEV.name
        ):
            try:
                resp = pvc_handler.delete_ingestion_directory(ValueStorage.folder_to_delete)
            except Exception as e:
                resp = None
                error_msg = str(e)
            assert (
                resp
            ), f"Test: [{test_exists_product_manual_ingestion.__name__}] Failed: on following ingestion process (Folder delete) :  [{error_msg}]"
            _log.info(f"Teardown - Finish PVC folder deletion")

        elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
            if os.path.exists(config.NFS_ROOT_DIR_DEST):
                shutil.rmtree(config.NFS_ROOT_DIR_DEST)
                _log.info(f"Teardown - Finish NFS folder deletion")

            else:
                raise NotADirectoryError(
                    f"Failed to delete directory because it doesnt exists: [{config.NFS_ROOT_DIR_DEST}]"
                )
        else:
            raise ValueError(f"Illegal environment value type: {config.TEST_ENV}")

        """ Clean up """
    # if config.CLEAN_UP and config.DEBUG_MODE_LOCAL:
    if config.DEBUG_MODE_LOCAL:
        for p in ValueStorage.discrete_list:
            cleanup_env(p["product_id"], p["product_version"], initial_mapproxy_config)


if config.DEBUG_MODE_LOCAL:
    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 4  # 4
if config.RUN_IT:
    test_exists_product_manual_ingestion()
