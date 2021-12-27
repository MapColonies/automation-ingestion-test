import logging
from time import sleep
from server_automation.configuration import config
from discrete_kit.validator.json_compare_pycsw import *
from discrete_kit.functions.shape_functions import ShapeToJSON
from server_automation.functions.executors import *
from server_automation.postgress import postgress_adapter
from conftest import ValueStorage

_log = logging.getLogger('server_automation.tests.test_invalid_imagery_data')


def test_invalid_data():
    stop_watch()
    try:
        resp = init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert resp, \
        f'Test: [{test_invalid_data.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]'
    _log.info(f'{resp}')

    product_id, product_version = resp['resource_name'].split('-')
    ValueStorage.discrete_list.append({'product_id': product_id, 'product_version': product_version})
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')
    sleep(5)

    if config.TEST_ENV == config.EnvironmentTypes.QA.name or config.TEST_ENV == config.EnvironmentTypes.DEV.name:
        pvc_handler = azure_pvc_api.PVCHandler(endpoint_url=config.PVC_HANDLER_ROUTE, watch=False)
        mock_resp = pvc_handler.create_mock_file(config.MOCK_IMAGERY_RAW_DATA_PATH, config.MOCK_IMAGERY_RAW_DATA_FILE)
    elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
        create_mock_file(config.MOCK_IMAGERY_RAW_DATA_PATH, config.MOCK_IMAGERY_RAW_DATA_FILE)
    # ToDo : Change the source of .tif for NFS

    try:
        status_code, content, source_data = start_manual_ingestion(source_directory, config.TEST_ENV)
    except Exception as e:
        status_code = 'unknown'
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, \
        f'Test: [{test_invalid_data.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n' \
        f'details: [{content}]'
    _log.info(f'manual ingestion - source_data: {source_data}')
    _log.info(f'manual ingestion - content: {content}')
    _log.info(f'manual ingestion - status code: {status_code}')
    sleep(config.SYSTEM_DELAY)
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info('Start following job-tasks based on job manager api')
            ingestion_follow_state = follow_running_job_manager(product_id, product_version)
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(product_id, product_version)
        resp = (ingestion_follow_state['status'] == config.JobStatus.Completed.name)
        error_msg = ingestion_follow_state['message']

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert not resp, \
        f'Test: [{test_invalid_data.__name__}] Failed: test should failed on generated tiles , msg :  [{error_msg}]'
    _log.info(f'Finished the test with invalid data , msg agent return :  [{error_msg}]')


test_invalid_data()
