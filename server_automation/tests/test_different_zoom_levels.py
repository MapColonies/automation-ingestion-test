import logging
from time import sleep
from server_automation.configuration import config
from server_automation.functions.executors import (
    stop_watch,
    init_ingestion_src,
    azure_pvc_api,
    start_manual_ingestion,
    s3,
    write_text_to_file
)
from server_automation.postgress import postgress_adapter
from conftest import ValueStorage

LIST_OBJECT_FROM_S_ = "Getting list object from S3"

CREATING_S_CLIENT = "Creating S3 client"

ZOOM_LEVEL_0_TO_4 = list(range(0, 5))
ZOOM_LEVEL_0_TO_10 = list(range(0, 11))
ZOOM_LEVEL_0_TO_16 = list(range(0, 17))

verification_list_0_to_4 = []
verification_list_0_to_10 = []
verification_list_0_to_16 = []

"""
 discreteOverseer.env.TILING_ZOOM_GROUPS = 0-5,6,7,8,9,10,11,12,13,14,15,16
"""

_log = logging.getLogger("server_automation.tests.test_different_zoom_levels")

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_zoom_level(zoom_lvl):
    _log.info("stopping watch")
    stop_watch()
    try:
        resp = init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_zoom_level.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
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
                        'test_name': test_zoom_level.__name__})
    _log.info(f"changing zoom to level : {zoom_lvl}")
    pvc_handler = azure_pvc_api.PVCHandler(
        endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
    )
    pvc_handler.change_max_zoom_tfw(zoom_lvl)
    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory, config.TEST_ENV, False
        )
        _log.info("finished manual ingestion")
    except Exception as e:
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_zoom_level.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}, expected :[{config.ResponseCode.Ok.value}]]"
    )

    _log.info(f"testing zoom to level : {zoom_lvl}")
    if zoom_lvl == config.FIRST_ZOOM_LEVEL:
        sleep(config.DIFFERENT_ZOOM_LEVEL_DELAY_4)
        _log.info(CREATING_S_CLIENT)
        s3_conn = s3.S3Client(
            config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY
        )
        s3_c = s3_conn.get_client()
        _log.info(LIST_OBJECT_FROM_S_)
        result = s3_c.list_objects(
            Bucket=config.S3_BUCKET_NAME,
            Prefix=f"{product_id}/{product_version}/OrthophotoHistory/",
            Delimiter="/",
        )
        _log.info(
            f"Got s3 files from product: {product_id} and id :{product_id} , result : {result}"
        )
        try:
            for o in result.get("CommonPrefixes"):
                verification_list_0_to_4.append(int(o.get("Prefix").split("/")[-2]))
            verification_list_0_to_4.sort()
        except IndexError as e:
            _log.error(f"Out of index in path , with msg {str(e)}")
            raise IndexError(f"Out of index in path , with msg {str(e)}")
        _log.info(f"sorted folders file from s3: {verification_list_0_to_4}")
        assert (
                verification_list_0_to_4 == ZOOM_LEVEL_0_TO_4
        ), f"Test: [{test_zoom_level.__name__}] Failed: on validation : actual [{verification_list_0_to_4} , expected {ZOOM_LEVEL_0_TO_4}]"

    elif zoom_lvl == config.SECOND_ZOOM_LEVEL:
        sleep(config.DIFFERENT_ZOOM_LEVEL_DELAY_10)
        _log.info(CREATING_S_CLIENT)
        s3_conn = s3.S3Client(
            config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY
        )
        s3_c = s3_conn.get_client()
        _log.info(LIST_OBJECT_FROM_S_)
        result = s3_c.list_objects(
            Bucket=config.S3_BUCKET_NAME,
            Prefix=f"{product_id}/{product_version}/OrthophotoHistory/",
            Delimiter="/",
        )
        _log.info(
            f"Got s3 files from product: {product_id} and id :{product_id} , result : {result}"
        )
        try:
            for o in result.get("CommonPrefixes"):
                verification_list_0_to_10.append(int(o.get("Prefix").split("/")[-2]))
            verification_list_0_to_10.sort()
        except IndexError as e:
            _log.error(f"Out of index in path , with msg {str(e)}")
            raise IndexError(f"Out of index in path , with msg {str(e)}")
        _log.info(f"sorted folders file from s3: {verification_list_0_to_10}")
        assert (
                verification_list_0_to_10 == ZOOM_LEVEL_0_TO_10
        ), f"Test: [{test_zoom_level.__name__}] Failed: on validation : actual [{verification_list_0_to_10} , expected {ZOOM_LEVEL_0_TO_10}]"

    elif zoom_lvl == config.THIRD_ZOOM_LEVEL:
        sleep(config.DIFFERENT_ZOOM_LEVEL_DELAY_16)
        _log.info(CREATING_S_CLIENT)
        s3_conn = s3.S3Client(
            config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY
        )
        s3_c = s3_conn.get_client()
        _log.info(LIST_OBJECT_FROM_S_)
        result = s3_c.list_objects(
            Bucket=config.S3_BUCKET_NAME,
            Prefix=f"{product_id}/{product_version}/OrthophotoHistory/",
            Delimiter="/",
        )
        _log.info(
            f"Got s3 files from product: {product_id} and id :{product_id} , result : {result}"
        )
        try:
            for o in result.get("CommonPrefixes"):
                verification_list_0_to_16.append(int(o.get("Prefix").split("/")[-2]))
            verification_list_0_to_16.sort()
        except IndexError as e:
            _log.error(f"Out of index in path , with msg {str(e)}")
            raise IndexError(f"Out of index in path , with msg {str(e)}")
        _log.info(f"sorted folders file from s3: {verification_list_0_to_16}")
        assert (
                verification_list_0_to_16 == ZOOM_LEVEL_0_TO_16
        ), f"Test: [{test_zoom_level.__name__}] Failed: on validation : actual [{verification_list_0_to_16} , expected {ZOOM_LEVEL_0_TO_16}]"
    else:
        raise Exception(f"Failed : unmatch zoom level , zoom level is {zoom_lvl}")


# if config.RUN_IT:
test_zoom_level(config.FIRST_ZOOM_LEVEL)
test_zoom_level(config.SECOND_ZOOM_LEVEL)
test_zoom_level(config.THIRD_ZOOM_LEVEL)
# if config.TEST_ENV == config.EnvironmentTypes.QA.name or config.TEST_ENV == config.EnvironmentTypes.DEV.name:
# elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
