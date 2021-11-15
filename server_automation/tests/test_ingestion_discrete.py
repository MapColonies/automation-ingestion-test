"""This module provide multiple test of ingestion services"""
import logging
import time
import json
from conftest import ValueStorage
from server_automation.configuration import config
from server_automation.functions import executors
from server_automation.postgress import postgress_adapter
from discrete_kit.validator.json_compare_pycsw import *
from server_automation.functions.executors import *
from discrete_kit.functions.shape_functions import ShapeToJSON

_log = logging.getLogger('server_automation.tests.test_ingestion_discrete')

initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_manual_discrete_ingest():
    """
    This test will test full e2e discrete ingestion
    """
    # config.TEST_ENV = 'PROD'
    config.PVC_UPDATE_ZOOM = False
    # prepare test data
    try:
        resp = executors.init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert resp, \
        f'Test: [{test_manual_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]'
    _log.info(f'{resp}')

    # triggering and validate start of new manuel job
    product_id, product_version = resp['resource_name'].split('-')
    ValueStorage.discrete_list.append({'product_id': product_id, 'product_version': product_version})
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')
    time.sleep(5)

    try:
        status_code, content, source_data = executors.start_manual_ingestion(source_directory, config.TEST_ENV)
    except Exception as e:
        status_code = 'unknown'
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, \
        f'Test: [{test_manual_discrete_ingest.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n' \
        f'details: [{content}]'

    # validating following and completion of ingestion job
    try:
        ingestion_follow_state = executors.follow_running_task(product_id, product_version)
        resp = (ingestion_follow_state['status'] == config.JobStatus.Completed.name)
        error_msg = ingestion_follow_state['message']

    except Exception as e:
        resp = None
        error_msg = str(e)

    # result, err = validate_pycsw_with_shape_json(get_json_schema('pycsw.json'), source_data)

    assert resp, \
        f'Test: [{test_manual_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]'

    time.sleep(config.FOLLOW_TIMEOUT)  # this timeout is for mapproxy updating time of new layer on configuration

    # validate new discrete on pycsw records
    try:
        resp, pycsw_record, links = executors.validate_pycsw2(product_id, product_version)
        # todo this is legacy records validator based graphql -> for future needs mabye
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp['validation']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)
    assert state, f'Test: [{test_manual_discrete_ingest.__name__}] Failed: validation of pycsw record\n' \
                  f'related errors:\n' \
                  f'{error_msg}'

    # validating new discrete on mapproxy
    try:
        resp = executors.validate_new_discrete(pycsw_record, product_id, product_version)
        state = resp['validation']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)

    assert state, f'Test: [{test_manual_discrete_ingest.__name__}] Failed: validation of mapproxy layer\n' \
                  f'related errors:\n' \
                  f'{error_msg}'

    if config.DEBUG_MODE_LOCAL:
        executors.test_cleanup(product_id, product_version, initial_mapproxy_config)


def test_watch_discrete_ingest():
    """
    This test ingestion by watching shared folder
    """

    # config.TEST_ENV = 'PROD'
    # stop watching folder as prerequisites
    try:
        resp = executors.stop_watch()
        state = resp['state']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)
    assert state, \
        f'Test: [{test_watch_discrete_ingest.__name__}] Failed: on stop agent watch [{error_msg}]'

    try:
        resp = executors.init_watch_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert resp, \
        f'Test: [{test_watch_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]'

    _log.info(f'{resp}')
    # triggering and validate start of new manuel job
    product_id, product_version = resp['resource_name'].split('-')
    ValueStorage.discrete_list.append({'product_id': product_id, 'product_version': product_version})
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')

    time.sleep(config.SYSTEM_DELAY)  # validate generation of new job
    # validating following and completion of ingestion job
    # ToDo: Uncomment this try catch
    # try:
    #     ingestion_follow_state = executors.follow_running_task(product_id, product_version)
    #     resp = (ingestion_follow_state['status'] == config.JobStatus.Completed.name)
    #     error_msg = ingestion_follow_state['message']
    #
    # except Exception as e:
    #     resp = None
    #     error_msg = str(e)
    # assert resp, \
    #     f'Test: [{test_watch_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]'
    # ToDo: Remove Comment for sleep
    # time.sleep(config.FOLLOW_TIMEOUT)  # this timeout is for mapproxy updating time of new layer on configuration

    # validate new discrete on pycsw records
    time.sleep(config.FOLLOW_TIMEOUT)
    try:
        shape_folder_path = executors.get_folder_path_by_name(source_directory, 'Shape')
        read_json_from_shape_file = ShapeToJSON(shape_folder_path)
        resp, pycsw_record, links = executors.validate_pycsw2(read_json_from_shape_file.created_json, product_id,
                                                              product_version)
        # todo this is legacy records validator based graphql -> for future needs mabye
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        # resp, pycsw_record, links = executors.validate_pycsw2(source_data, product_id, product_version)
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp['validation']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)
    # ToDo: Uncomment it before pushing
    # assert state, f'Test: [{test_manual_discrete_ingest.__name__}] Failed: validation of pycsw record\n' \
    #               f'related errors:\n' \
    #               f'{error_msg}'

    # assert state, f'Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of pycsw record\n' \
    #               f'related errors:\n' \
    #               f'{error_msg}'

    # validating new discrete on mapproxy
    try:
        resp = executors.validate_new_discrete(pycsw_record, product_id, product_version)
        state = resp['validation']
        error_msg = resp['reason']
    except Exception as e:
        state = False
        error_msg = str(e)

    ##### enable after new version of ingestion with mapproxy live update

    assert state, f'Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of mapproxy layer\n' \
                  f'related errors:\n' \
                  f'{error_msg}'
    resp = executors.stop_watch()
    _log.info(f'Finish running watch ingestion. Watch status: [{resp["reason"]}]')
    if config.DEBUG_MODE_LOCAL:
        executors.test_cleanup(product_id, product_version, initial_mapproxy_config)


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """
    executors.stop_watch()
    if config.CLEAN_UP:
        for p in ValueStorage.discrete_list:
            executors.test_cleanup(p['product_id'], p['product_version'], initial_mapproxy_config)


if config.DEBUG_MODE_LOCAL:
    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 4

    # test_manuel_discrete_ingest()
    test_watch_discrete_ingest()

# from server_automation.pycsw import pycsw_handler
# res = pycsw_handler.get_record_by_id('2021_10_26T11_03_39Z_MAS_6_ORT_247993', '1.0', host=config.PYCSW_URL, params=config.PYCSW_GET_RECORD_PARAMS)
# res = pycsw_handler.get_raster_records()
