"""This module provide multiple test of ingestion services"""
import logging
from conftest import ValueStorage
import os
from server_automation.configuration import config
from server_automation.functions import executors
from server_automation.postgress import postgress_adapter
from server_automation.ingestion_api import discrete_directory_loader
from mc_automation_tools import common as common

_log = logging.getLogger('server_automation.tests.test_ingestion_discrete')

initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_new_discrete_ingest():
    """
    This test will test full e2e discrete ingestion
    """
    # config.TEST_ENV = 'PROD'
    # prepare test data


    try:
        resp = executors.init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert resp, \
        f'Test: [{test_new_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]'

    _log.info(f'{resp}')
    # triggering new ingestion
    product_id, product_version = resp['resource_name'].split('-')
    ValueStorage.discrete_list.append({'product_id': product_id, 'product_version': product_version})
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')
    try:
        status_code, content = executors.start_manuel_ingestion(source_directory, config.TEST_ENV)
    except Exception as e:
        status_code = 'unknown'
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, \
        f'Test: [{test_new_discrete_ingest.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n' \
        f'details: [{content}]'

    resp = executors.follow_running_task(product_id, product_version)
    if config.DEBUG_MODE_LOCAL:
        executors.test_cleanup(product_id, product_version, initial_mapproxy_config)


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """

    for p in ValueStorage.discrete_list:
        executors.test_cleanup(p['product_id'], p['product_version'], initial_mapproxy_config)
    print("\nenvironment was cleaned up")


if config.DEBUG_MODE_LOCAL:
    test_new_discrete_ingest()