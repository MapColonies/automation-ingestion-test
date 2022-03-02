import logging
from time import sleep
from discrete_kit.functions.shape_functions import ShapeToJSON
from server_automation.configuration import config
from server_automation.functions.executors import stop_watch, init_ingestion_src, write_text_to_file, azure_pvc_api, \
    create_mock_file, start_manual_ingestion, follow_running_task, follow_running_job_manager
from server_automation.postgress import postgress_adapter
from conftest import ValueStorage

_log = logging.getLogger("server_automation.tests.test_invalid_imagery_data")


def test_invalid_data():
    stop_watch()
    try:
        resp = init_ingestion_src()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_invalid_data.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")

    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )

    source_directory = resp["ingestion_dir"]
    _log.info("%s %s", product_id, product_version)
    if config.WRITE_TEXT_TO_FILE:
        write_text_to_file('//tmp//shlomo.txt',
                           {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                            'test_name': test_invalid_data.__name__})
    sleep(5)
    if config.SOURCE_DATA_PROVIDER.lower() == 'pv':
        pvc_handler = azure_pvc_api.PVCHandler(
            endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
        )
        pvc_handler.create_mock_file(
            config.MOCK_IMAGERY_RAW_DATA_PATH_PVC, config.MOCK_IMAGERY_RAW_DATA_FILE_PVC
        )
    if config.SOURCE_DATA_PROVIDER.lower() == 'nfs':
        create_mock_file(
            config.MOCK_IMAGERY_RAW_DATA_PATH, config.MOCK_IMAGERY_RAW_DATA_FILE
        )
    # ToDo : Change the source of .tif for NFS

    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory
        )
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_invalid_data.__name__}] "
        f"Failed: trigger new ingest with status: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info("manual ingestion - source_data: %s", source_data)
    _log.info("manual ingestion - content: %s", content)
    _log.info("manual ingestion - status code: %s", status_code)
    sleep(config.DELAY_INVALID_IMAGE_TEST)
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
        not resp
    ), f"Test: [{test_invalid_data.__name__}] Failed: test should failed on generated tiles , msg :  [{error_msg}]"
    _log.info(
        f"Finished the test with invalid data , msg agent return :  [{error_msg}]"
    )

#
# if config.RUN_IT:
#     test_invalid_data()
