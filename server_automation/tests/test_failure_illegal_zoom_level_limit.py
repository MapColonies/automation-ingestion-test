import logging
from time import sleep
from server_automation.configuration import config
from server_automation.functions.executors import *
from conftest import ValueStorage

_log = logging.getLogger(
    "server_automation.tests.test_failure_illegal_zoom_level_limit"
)


def test_illegal_zoom():
    stop_watch()
    try:
        resp = init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_illegal_zoom.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")

    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp["ingestion_dir"]
    _log.info(f"{product_id} {product_version}")
    sleep(5)

    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 3  # 4
    pvc_handler = azure_pvc_api.PVCHandler(
        endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
    )
    pvc_handler.change_max_zoom_tfw(config.MAX_ZOOM_TO_CHANGE)
    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory, config.TEST_ENV, False
        )
    except Exception as e:
        content = str(e)
    assert status_code == config.ResponseCode.ValidationErrors.value, (
        f"Test: [{test_illegal_zoom.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}, expected :[{config.ResponseCode.ValidationErrors.value}]]"
    )


test_illegal_zoom()
