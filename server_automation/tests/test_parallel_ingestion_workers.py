import logging
from server_automation.configuration import config
from server_automation.functions.executors import *
from conftest import ValueStorage
from time import sleep

_log = logging.getLogger('server_automation.tests.test_ingestion_discrete')

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_parallel_ingestion():
    try:
        resp = init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert resp, \
        f'Test: [{test_parallel_ingestion.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]'
    _log.info(f'{resp}')

    product_id, product_version = resp['resource_name'].split('-')
    ValueStorage.discrete_list.append({'product_id': product_id, 'product_version': product_version})
    source_directory = resp['ingestion_dir']
    _log.info(f'{product_id} {product_version}')
    sleep(5)
    # ================================================================================================================ #
    try:
        status_code, content, source_data = start_manual_ingestion(source_directory, config.TEST_ENV)
    except Exception as e:
        status_code = 'unknown'
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, \
        f'Test: [{test_parallel_ingestion.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n' \
        f'details: [{content}]'
    _log.info(f'manual ingestion - source_data: {source_data}')
    _log.info(f'manual ingestion - content: {content}')
    _log.info(f'manual ingestion - status code: {status_code}')
    # ================================================================================================================ #

    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info('Start following job-tasks based on job manager api')
            sleep(config.PROGRESS_TASK_DELAY)
            ingestion_in_progress_state = follow_parallel_running_tasks(product_id, product_version)

    except Exception as e:
        resp = None
        error_msg = str(e)
    if error_msg is None:
        error_msg = 'Workers not equal to progress tasks'
    num_tasks = ingestion_in_progress_state['in_progress_tasks']
    resp = (ingestion_in_progress_state['status'] == config.JobStatus.Completed.name)
    error_msg = ingestion_in_progress_state['message']

    assert resp, \
        f'Test: [{test_parallel_ingestion.__name__}] Failed: on following ingestion process [{error_msg}]'
    _log.info(f'manual ingestion following task response: {resp}')

    assert (num_tasks == config.AMOUNT_OF_WORKERS), \
        f'Test: [{test_parallel_ingestion.__name__}] Failed: on following ingestion process [{error_msg} , actually {num_tasks} but expected : {config.AMOUNT_OF_WORKERS}]'
    _log.info(f'manual ingestion following task response: {resp}')
    _log.info(f'finished parallel test for : {config.AMOUNT_OF_WORKERS} workers (tasks number in parallel)')
    sleep(config.SYSTEM_DELAY)  # this timeout is for mapproxy updating time of new layer on configuration

    if config.DEBUG_MODE_LOCAL:
        cleanup_env(product_id, product_version, initial_mapproxy_config)


if config.DEBUG_MODE_LOCAL:
    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 14  # 4

test_parallel_ingestion()
