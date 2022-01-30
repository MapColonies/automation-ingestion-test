import logging
import json
import os.path
from time import sleep
from conftest import ValueStorage
from server_automation.functions.executors import *
from server_automation.postgress import postgress_adapter
from mc_automation_tools.ingestion_api import overseer_api
from mc_automation_tools.validators import pycsw_validator
import random
import string

from discrete_kit.functions.shape_functions import ShapeToJSON

_log = logging.getLogger("server_automation.tests.test_manual_geopackage_ingestion")


def test_manual_ingestion_geopackage():
    stop_watch()

    # ToDo: Copy GeoPack file to Folder
    status_code, resp = copy_geopackage_file_for_ingest(config.TEST_ENV)
    src_folder_to_copy = resp['source']
    assert (
            status_code == config.ResponseCode.ChangeOk.value
    ), f"Test: [{test_manual_ingestion_geopackage.__name__}] Failed: on copy src {src_folder_to_copy} status code :  [{status_code}]"
    _log.info(f"Finished - copy {src_folder_to_copy} to watch folder")

    # ToDo: Start Manual ingestion with api
    os_manager = overseer_api.Overseer(
        end_point_url=config.OVERSEER_END_URL)
    os_param = config.OVERSEER_JSON_LOCATION
    try:
        with open(os_param, "r", encoding="utf-8") as fp:
            params = json.load(fp)
    except Exception as e:
        raise EnvironmentError("Failed to load JSON for configuration") from e
    letters = string.ascii_lowercase

    my_json = ShapeToJSON().create_metadata_from_toc(params['metadata'])
    # pycsw_conn = pycsw_validator.PycswHandler(pycsw_url, query_params)
    # results = pycsw_conn.validate_pycsw(toc_json, layer_id, layer_version)
    product_name = (''.join(random.choice(letters) for i in range(10)))
    params['metadata']['productId'] = product_name
    my_json['productId']['value'] = product_name
    if (
            config.TEST_ENV == config.EnvironmentTypes.QA.name
            or config.TEST_ENV == config.EnvironmentTypes.DEV.name
    ):
        params['originDirectory'] = config.GEO_PACKAGE_DEST_PVC
    if config.TEST_ENV == config.EnvironmentTypes.PROD.name:
        params['originDirectory'] = config.GEO_PACKAGE_DEST_NFS

    resp, body = os_manager.create_layer(params)

    body_json = json.loads(body)
    print(body_json['metadata']['productId'])
    # print(product_name)
    # print("da")
    assert (
            resp == config.ResponseCode.Ok.value
    ), f"Test: [{test_manual_ingestion_geopackage.__name__}] Failed: on creating layer , status code : {resp}, body:{body}"

    # ToDo: Record validation
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            ingestion_follow_state = follow_running_job_manager(
                body_json['metadata']['productId'], body_json['metadata']['productVersion']
            )
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(body_json['metadata']['productId'],
                                                         body_json['metadata']['productVersion'])
            _log.info("Start following job-tasks based on bff api")
        resp = ingestion_follow_state["status"] == config.JobStatus.Completed.name
        error_msg = ingestion_follow_state["message"]

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_manual_ingestion_geopackage.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"watch ingestion following task response:{resp}")

    # ToDo: Validate pycsw record
    try:
        # shape_folder_path = executors.get_folder_path_by_name(source_directory, 'Shape')
        # read_json_from_shape_file = ShapeToJSON(shape_folder_path)
        # pycsw_record, links
        resp, pycsw_record, links = validate_geopack_pycsw({"metadata": my_json},
                                                           body_json['metadata']['productId'],
                                                           body_json['metadata']['productVersion']
                                                           )
        # todo this is legacy records validator based graphql -> for future needs maybe
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp['validation']
        error_msg = resp["reason"]
        reason_e = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)
        _log.error(f'error : {error_msg}')
    assert (
        state
    ), f"Test: [{test_manual_ingestion_geopackage.__name__}] Failed: on validation, error msg : {reason_e}, exception:{error_msg}"

    try:
        resp = validate_new_discrete(pycsw_record, body_json['metadata']['productId'],
                                     body_json['metadata']['productVersion'])
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)
        _log.error(f'error : {error_msg}')
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
