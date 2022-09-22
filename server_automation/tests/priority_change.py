import logging
from time import sleep

from mc_automation_tools.parse.stringy import pad_with_minus
from mc_automation_tools.parse.stringy import pad_with_stars

from conftest_val import ValueStorage
from server_automation.configuration import config
from server_automation.functions.executors import *
from server_automation.functions.executors import stop_watch

_log = logging.getLogger("server_automation.tests.test_priority_change")


def test_priority_change():
    # ToDo : JobManager API
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
                "test_name": test_priority_change.__name__,
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
        f"Test: [{test_priority_change.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info(f"manual ingestion - source_data: {source_data}")
    _log.info(f"manual ingestion - content: {content}")
    _log.info(f"manual ingestion - status code: {status_code}")
    _log.info("\n" + pad_with_minus("Finished - manual ingestion"))
    return
    # # ToDo: Ingest Job First Job- High Resolution
    # sleep(config.DELAY_PRIORITY_FIRST_JOB)
    #
    # # ToDo: Ingest Second Job With Higher Priority- High Resolution
    # sleep(config.DELAY_PRIORITY_SECOND_JOB)

    # Todo: Check Job 2 is In Progress.. Before job 1

    assert True  # ToDo : Fix It compare it status code and more. add more assertions.


def init_ingestion_folder():
    if config.SOURCE_DATA_PROVIDER.lower() == "pv":
        return pv_init_ingestion_flow(False)
    if config.SOURCE_DATA_PROVIDER.lower() == "nfs":
        return nfs_init_ingestion_flow()
    else:
        raise ValueError(
            f"Illegal environment value type: {config.SOURCE_DATA_PROVIDER.lower()}"
        )


def init_ingestion_folder_without_delete():
    _log.info("\n" + pad_with_stars("Started - init_ingestion_folder"))
    try:
        resp = init_ingestion_src_for_priority()
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_priority_change.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"Response [init_ingestion_src] : {resp}")
    _log.info(pad_with_minus("Finished - init_ingestion_folder"))
    return resp


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


def pv_init_ingestion_flow(delete_folder=False):
    _log.info("\n" + pad_with_stars("Started - create ingestion folder"))
    try:
        destination_folder, resp_code = create_ingestion_folder_pvc(
            False, delete_folder
        )
    except RuntimeError as err:
        create_folder_err = str(err)

    assert (
        resp_code.status_code == config.ResponseCode.ChangeOk.value
    ), f"Test: [{test_priority_change.__name__}] Failed: create folder with status code: [{resp_code.status_code}],details : [{create_folder_err}]"
    _log.info("\n" + pad_with_stars("Finished - create ingestion folder"))

    _log.info("\n" + pad_with_stars("Started - update ingestion source name"))
    try:
        updated_source_name, resp_code = update_ingestion_folder_pvc(False)
    except Exception as err:
        update_source_name_err = str(err)

    assert (
        resp_code.status_code == config.ResponseCode.ChangeOk.value
    ), f"Test: [{test_priority_change.__name__}] Failed: update source name with status code: [{resp_code.status_code}],details : [{update_source_name_err}] "
    _log.info("\n" + pad_with_stars("Finished - update ingestion source name"))

    _log.info("\n" + pad_with_stars("Started - change zoom level"))
    try:
        resp_code = change_zoom_level_pvc(config.THIRD_ZOOM_LEVEL)
    except Exception as err:
        change_zoom_err = str(err)
    assert (
        resp_code.status_code == config.ResponseCode.Ok.value
    ), f"Test: [{test_priority_change.__name__}] Failed: change zoom with status code: [{resp_code.status_code}],details : [{change_zoom_err}] "
    _log.info("\n" + pad_with_stars("Finished - change zoom level"))
    return destination_folder, updated_source_name


test_priority_change()
