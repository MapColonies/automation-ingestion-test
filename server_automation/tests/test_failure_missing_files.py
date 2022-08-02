import logging
from time import sleep
from server_automation.configuration import config
from server_automation.functions.executors import stop_watch, init_ingestion_src, delete_file_from_folder, \
    write_text_to_file, start_manual_ingestion
from conftest_val import ValueStorage

_log = logging.getLogger("server_automation.tests.test_failure_missing_files")

list_of_missing_files = ["Files.shp", "ShapeMetadata.shp", "*.tif", "*.tfw"]


def test_missing_files():
    for missing_file in list_of_missing_files:

        stop_watch()
        try:
            resp = init_ingestion_src()
            error_msg = None
        except Exception as e:
            resp = None
            error_msg = str(e)
        assert (
            resp
        ), f"Test: [{test_missing_files.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
        _log.info(f"{resp}")

        product_id, product_version = resp["resource_name"].split("-")
        ValueStorage.discrete_list.append(
            {"product_id": product_id, "product_version": product_version}
        )
        source_directory = resp["ingestion_dir"]
        _log.info(f"{product_id} {product_version}")
        sleep(5)

        if config.WRITE_TEXT_TO_FILE:
            write_text_to_file('//tmp//shlomo.txt',
                               {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                                'test_name': test_missing_files.__name__})

        delete_file_from_folder(source_directory, missing_file)

        try:
            status_code, content, source_data = start_manual_ingestion(
                source_directory
                , False
            )
        except Exception as e:
            content = str(e)
        assert status_code == config.ResponseCode.ValidationErrors.value, (
            f"Test: [{test_missing_files.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
            f"details: [{content}, expected :[{config.ResponseCode.ValidationErrors.value}]]"
        )


if config.RUN_IT:
    test_missing_files()
