import logging
from server_automation.functions.executors import stop_watch
from time import sleep
from server_automation.configuration import config
from server_automation.functions.executors import *
from conftest import ValueStorage
from mc_automation_tools.parse.stringy import pad_with_minus, pad_with_stars

_log = logging.getLogger("server_automation.tests.test_priority_change")


def test_priority_change():
    stop_watch()

    resp_from_init_folder = init_ingestion_folder()

    product_id, product_version = resp_from_init_folder["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp_from_init_folder["ingestion_dir"]
    _log.info(f"Product_id : {product_id} , Product_version : {product_version}")
    sleep(5)

    if config.WRITE_TEXT_TO_FILE:
        _log.info("Starting - Write Tests to files.................")
        write_text_to_file('//tmp//test_runs.txt',
                           {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                            'test_name': test_priority_change.__name__,
                            'folder_to_delete': ValueStorage.folder_to_delete})
        _log.info("Finished - Write Tests to files.................")

    _log.info(f'Starting - manual ingestion...............')
    try:
        status_code, content, source_data = start_manual_ingestion(source_directory)
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_priority_change.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    # ToDo: Ingest Job First Job- High Resolution
    sleep(config.DELAY_PRIORITY_FIRST_JOB)

    # ToDo: Ingest Second Job With Higher Priority- High Resolution
    sleep(config.DELAY_PRIORITY_SECOND_JOB)

    # Todo: Check Job 2 is In Progress.. Before job 1

    assert True  # ToDo : Fix It compare it status code and more. add more assertions.

def init_ingestion_folder():
    _log.info('\n' + pad_with_stars('Started - init_ingestion_folder'))
    try:
        resp = init_ingestion_src()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_priority_change.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"Response [init_ingestion_src] : {resp}")
    _log.info(pad_with_minus('Finished - init_ingestion_folder'))
    return resp



test_priority_change()
