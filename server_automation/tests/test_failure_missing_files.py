import logging
from time import sleep
from server_automation.functions.executors import *
from conftest import ValueStorage

_log = logging.getLogger("server_automation.tests.test_failure_missing_files")

list_of_missing_files = ["Files.shp", "ShapeMetadata.shp", "*.tif", "*.tfw"]


def test_missing_files():
    for missing_file in list_of_missing_files:

        stop_watch()
        try:
            resp = init_ingestion_src(config.TEST_ENV)
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

        write_text_to_file('//tmp//shlomo.txt',
                           {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                            'test_name': test_missing_files.__name__})

        delete_file_from_folder(source_directory, missing_file, config.TEST_ENV)

        try:
            status_code, content, source_data = start_manual_ingestion(
                source_directory, config.TEST_ENV, False
            )
        except Exception as e:
            content = str(e)
        assert status_code == config.ResponseCode.ValidationErrors.value, (
            f"Test: [{test_missing_files.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
            f"details: [{content}, expected :[{config.ResponseCode.ValidationErrors.value}]]"
        )

    # ToDo : Create new source data -> copy and edit origin discrete- unique
    # product name

    # ToDo : copy the data and remove tiff files

    # ToDo : Start manual ingestion via manual post request [rest api]

    # ToDo : Check if Status 400 - bad request -> No(Test Failed)

    # ToDo: copy full source data instead of previous - remove
    # shapemetadata.shp files

    # ToDo : Start manual ingestion via manual post request [rest api]

    # ToDo : Check if Status 400 - bad request -> No(Test Failed)

    # ToDo: copy full source data instead of previous - remove files.shp files

    # ToDo : Start manual ingestion via manual post request [rest api]

    # ToDo : Check if Status 400 - bad request -> No(Test Failed)

    # ToDo: copy full source data instead of previous - remove tfw.shp files

    # ToDo : Start manual ingestion via manual post request [rest api]

    # ToDo : Check if Status 400 - bad request -> No(Test Failed)

    # ToDo Test Finished Successfully
if config.RUN_IT:
    test_missing_files()
