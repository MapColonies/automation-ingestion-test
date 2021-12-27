import logging
from server_automation.configuration import config
from server_automation.functions.executors import *
from server_automation.postgress import postgress_adapter
from time import sleep
from conftest import ValueStorage

_log = logging.getLogger('server_automation.tests.test_different_zoom_levels')

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_ingestion_with_zoom_level(zoom_level_to_test):
    stop_watch()
    try:
        resp = init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert resp, \
        f'Test: [{test_ingestion_with_zoom_level.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]'
    _log.info(f'{resp}')

    product_id, product_version = resp['resource_name'].split('-')
    ValueStorage.discrete_list.append({'product_id': product_id, 'product_version': product_version})
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')
    sleep(5)

    # config.PVC_UPDATE_ZOOM = True
    # config.MAX_ZOOM_TO_CHANGE = zoom_level_to_test
    pvc_handler = azure_pvc_api.PVCHandler(endpoint_url=config.PVC_HANDLER_ROUTE, watch=False)
    pvc_handler.change_max_zoom_tfw(config.MAX_ZOOM_TO_CHANGE)
    try:
        status_code, content, source_data = start_manual_ingestion(source_directory, config.TEST_ENV, False)
    except Exception as e:
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, \
        f'Test: [{test_ingestion_with_zoom_level.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n' \
        f'details: [{content}, expected :[{config.ResponseCode.Ok.value}]]'

    sleep(config.DIFFERENT_ZOOM_LEVEL_DELAY)

    try:
        resp, pycsw_record, links = validate_pycsw(source_data, product_id, product_version)
        # todo this is legacy records validator based graphql -> for future needs maybe
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp['validation']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, f'Test: [{test_ingestion_with_zoom_level.__name__}] Failed: validation of pycsw record\n' \
                      f'related errors:\n' \
                      f'{error_msg}'
        _log.info(f'manual ingestion validation - response: {resp}')
        _log.info(f'manual ingestion validation - pycsw_record: {pycsw_record}')
        _log.info(f'manual ingestion validation - links: {links}')

    try:
        resp = validate_new_discrete(pycsw_record, product_id, product_version)
        state = resp['validation']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, f'Test: [{test_ingestion_with_zoom_level.__name__}] Failed: validation of mapproxy layer\n' \
                      f'related errors:\n' \
                      f'{error_msg}'
        _log.info(f'manual ingestion validate new discrete - response: {resp}')


test_ingestion_with_zoom_level(13)
# test_ingestion_with_zoom_level(4)
# test_ingestion_with_zoom_level(4)
