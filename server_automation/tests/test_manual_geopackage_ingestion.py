import logging
import json
from time import sleep
from conftest import ValueStorage
from server_automation.functions.executors import *
from server_automation.postgress import postgress_adapter
from mc_automation_tools.ingestion_api import overseer_api
import random
import string

_log = logging.getLogger("server_automation.tests.test_manual_geopackage_ingestion")


def test_manual_ingestion_geopackage():
    stop_watch()

    # ToDo: Validate file exists - Geopack
    # ToDo: Copy GeoPack file to Folder

    # ToDo: Start Manual ingestion with api
    os = overseer_api.Overseer(
        end_point_url='')
    os_param =''
    try:
        with open(os_param, "r", encoding="utf-8") as fp:
            params = json.load(fp)
    except Exception as e:
        raise EnvironmentError("Failed to load JSON for configuration") from e
    letters = string.ascii_lowercase
    product_name = (''.join(random.choice(letters) for i in range(10)))
    params['metadata']['productId'] = product_name
    resp, body = os.create_layer(params)
    body_json = json.loads(body)
    print(body_json['metadata']['productId'])
    print("da")

    # ToDo: verify status is 200
    # ToDo: Record validation
    # ToDo: Validate pycsw record
    # ToDo: New discrete mapproxy
    """
    After getting ok ,
    verify job is created
        try:
        resp = executors.validate_sync_job_creation(ingestion_product_id,
                                                    ingestion_product_version,
                                                    config.JobTaskTypes.SYNC_TRIGGER.value,
                                                    job_manager_url=config.JOB_MANAGER_ROUTE_CORE_A)
        msg = resp['message']
        sync_job_state = resp['state']
        sync_job = resp['record']

    except Exception as e:
        sync_job_state = False
        msg = str(e)

    assert sync_job_state, f'Test: [{test_trigger_to_gw.__name__}] Failed: Query for new sync job\n' \
                           f'related errors:\n' \
                           f'{msg}'



    follow job

      sync_job = sync_job[0]
    sync_job_id = sync_job['id']
    cleanup_data['sync_job_id'] = sync_job_id

    try:
        resp = executors.follow_sync_job(product_id=ingestion_product_id,
                                         product_version=ingestion_product_version,
                                         product_type=config.JobTaskTypes.SYNC_TRIGGER.value,
                                         job_manager_url=config.JOB_MANAGER_ROUTE_CORE_A,
                                         running_timeout=config.SYNC_TIMEOUT,
                                         internal_timeout=config.BUFFER_TIMEOUT_CORE_A)
        sync_follow_state = True if resp['status'] == config.JobStatus.Completed.value else False
        msg = resp['message']
    except Exception as e:
        sync_follow_state = False
        msg = str(e)
    assert sync_follow_state, f'Test: [{test_trigger_to_gw.__name__}] Failed: Follow for sync job complete\n' \
                              f'related errors:\n' \
                              f'{msg}'z



    validation




    """


test_manual_ingestion_geopackage()