"""This module provide multiple test of ingestion services"""
import logging
import os
from server_automation.configuration import config
from server_automation.functions import executors
from server_automation.ingestion_api import discrete_directory_loader
from mc_automation_tools import common as common

_log = logging.getLogger('server_automation.tests.test_ingestion_discrete')


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
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')
    resp = executors.start_manuel_ingestion(source_directory, config.TEST_ENV)




test_new_discrete_ingest()