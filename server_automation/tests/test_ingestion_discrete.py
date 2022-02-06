"""This module provides multiple test of ingestion services"""
import shutil
from time import sleep
from conftest import ValueStorage
import logging
import json
from server_automation.configuration import config
from discrete_kit.validator.json_compare_pycsw import *
from discrete_kit.functions.shape_functions import ShapeToJSON
from server_automation.functions.executors import *
from server_automation.postgress import postgress_adapter

_log = logging.getLogger("server_automation.tests.test_ingestion_discrete")

if config.DEBUG_MODE_LOCAL:
    initial_mapproxy_config = postgress_adapter.get_mapproxy_configs()


def test_manual_discrete_ingest():
    """
    This test will test full e2e discrete ingestion
    """
    stop_watch()
    try:
        resp = init_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")

    # triggering and validate start of new manuel job
    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp["ingestion_dir"]
    _log.info(f"{product_id} {product_version}")
    sleep(5)

    write_text_to_file('//tmp//shlomo.txt',
                       {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                        'test_name': test_manual_discrete_ingest.__name__,
                        'folder_to_delete': ValueStorage.folder_to_delete})

    try:
        status_code, content, source_data = start_manual_ingestion(
            source_directory, config.TEST_ENV
        )
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert status_code == config.ResponseCode.Ok.value, (
        f"Test: [{test_manual_discrete_ingest.__name__}] Failed: trigger new ingest with status code: [{status_code}]\n"
        f"details: [{content}]"
    )
    _log.info(f"manual ingestion - source_data: {source_data}")
    _log.info(f"manual ingestion - content: {content}")
    _log.info(f"manual ingestion - status code: {status_code}")

    # validating following and completion of ingestion job
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            ingestion_follow_state = follow_running_job_manager(
                product_id, product_version
            )
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(product_id, product_version)
        resp = ingestion_follow_state["status"] == config.JobStatus.Completed.name
        error_msg = ingestion_follow_state["message"]

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_manual_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"manual ingestion following task response: {resp}")

    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.DELAY_INGESTION_TEST)
    pycsw_record = None

    # validate new discrete on pycsw records
    try:
        resp, pycsw_record, links = validate_pycsw2(
            source_data, product_id, product_version
        )
        # todo this is legacy records validator based graphql -> for future needs maybe
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_manual_discrete_ingest.__name__}] Failed: validation of pycsw record\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        _log.info(f"manual ingestion validation - response: {resp}")
        _log.info(f"manual ingestion validation - pycsw_record: {pycsw_record}")
        _log.info(f"manual ingestion validation - links: {links}")

    # validating new discrete on mapproxy
    try:
        resp = validate_new_discrete(pycsw_record, product_id, product_version)
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_manual_discrete_ingest.__name__}] Failed: validation of mapproxy layer\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        _log.info(f"manual ingestion validate new discrete - response: {resp}")

    if config.DEBUG_MODE_LOCAL:
        cleanup_env(product_id, product_version, initial_mapproxy_config)


def test_watch_discrete_ingest():
    """
    This test ingestion by watching shared folder
    """
    # config.TEST_ENV = 'PROD'
    # stop watching folder as prerequisites
    try:
        resp = stop_watch()
        state = resp["state"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)
    assert (
        state
    ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on stop agent watch [{error_msg}]"
    _log.info(f"watch ingestion - stop watch response: {resp}")

    try:
        resp = init_watch_ingestion_src(config.TEST_ENV)
        error_msg = None
    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on creating and updating layerSource folder [{error_msg}]"
    _log.info(f"{resp}")
    # triggering and validate start of new manuel job
    product_id, product_version = resp["resource_name"].split("-")
    ValueStorage.discrete_list.append(
        {"product_id": product_id, "product_version": product_version}
    )
    source_directory = resp["ingestion_dir"]
    ValueStorage.folder_to_delete = source_directory.split("/watch/")[-1]
    _log.info(f"{product_id} {product_version}")
    _log.info(f"watch ingestion init - source_directory: {source_directory}")
    write_text_to_file('//tmp//shlomo.txt',
                       {'source_dir': source_directory, 'product_id_version': ValueStorage.discrete_list,
                        'test_name': test_watch_discrete_ingest.__name__,
                        'folder_to_delete': ValueStorage.folder_to_delete})
    try:
        state, content, source_data = start_watch_ingestion(
            source_directory, config.TEST_ENV
        )
    except Exception as e:
        status_code = "unknown"
        content = str(e)
    assert state, (
        f"Test: [{test_watch_discrete_ingest.__name__}] Failed: Trigger ingest process from watch agent: [{status_code}]\n"
        f"details: [{content}]"
    )

    _log.info(f"watch ingestion ,start watch - state: {state}")
    _log.info(f"watch ingestion ,start watch - content: {content}")
    _log.info(f"watch ingestion ,start watch - source_data: {source_data}")

    sleep(config.DELAY_INGESTION_TEST)  # validate generation of new job
    # validating following and completion of ingestion job
    try:
        if config.FOLLOW_JOB_BY_MANAGER:  # following based on job manager api
            _log.info("Start following job-tasks based on job manager api")
            ingestion_follow_state = follow_running_job_manager(
                product_id, product_version
            )
        else:  # following based on bff service
            ingestion_follow_state = follow_running_task(product_id, product_version)
            _log.info("Start following job-tasks based on bff api")
        resp = ingestion_follow_state["status"] == config.JobStatus.Completed.name
        error_msg = ingestion_follow_state["message"]

    except Exception as e:
        resp = None
        error_msg = str(e)
    assert (
        resp
    ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on following ingestion process [{error_msg}]"
    _log.info(f"watch ingestion following task response:{resp}")

    # this timeout is for mapproxy updating time of new layer on configuration
    sleep(config.DELAY_INGESTION_TEST * 2)
    pycsw_record = None
    # validate new discrete on pycsw records
    try:

        resp, pycsw_record, links = validate_pycsw2(
            source_data, product_id, product_version
        )
        # todo this is legacy records validator based graphql -> for future needs maybe
        # resp, pycsw_record = executors.validate_pycsw(config.GQK_URL, product_id, source_data)
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of pycsw record\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        _log.info(f"watch ingestion ,watch validation - response: {resp}")
        _log.info(f"watch ingestion ,watch validation - pycsw_record: {pycsw_record}")
        _log.info(f"watch ingestion ,watch validation - links: {links}")

    # validating new discrete on mapproxy
    try:
        resp = validate_new_discrete(pycsw_record, product_id, product_version)
        state = resp["validation"]
        error_msg = resp["reason"]
    except Exception as e:
        state = False
        error_msg = str(e)

    if config.VALIDATION_SWITCH:
        assert state, (
            f"Test: [{test_watch_discrete_ingest.__name__}] Failed: validation of mapproxy layer\n"
            f"related errors:\n"
            f"{error_msg}"
        )
        resp = stop_watch()
        _log.info(
            f'watch ingestion, Finish running watch ingestion. Watch status: [{resp["reason"]}]'
        )


def teardown_module(module):  # pylint: disable=unused-argument
    """
    This method been executed after test running - env cleaning
    """
    stop_watch()
    pvc_handler = azure_pvc_api.PVCHandler(
        endpoint_url=config.PVC_HANDLER_ROUTE, watch=False
    )
    if config.CLEAN_UP and config.VALIDATION_SWITCH:
        if (
                config.TEST_ENV == config.EnvironmentTypes.QA.name
                or config.TEST_ENV == config.EnvironmentTypes.DEV.name
        ):
            # ToDo : Handle PVC - test it
            try:
                error_msg = None
                resp = pvc_handler.delete_ingestion_directory(
                    api=config.PVC_DELETE_DIR

                )
            except Exception as e:
                resp = None
                error_msg = str(e)
            assert (
                resp
            ), f"Test: [{test_watch_discrete_ingest.__name__}] Failed: on following ingestion process (Folder delete) :  [{error_msg}]"
            _log.info(f"Teardown - Finish PVC folder deletion")

        elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
            if os.path.exists(config.NFS_ROOT_DIR_DEST):
                shutil.rmtree(config.NFS_ROOT_DIR_DEST)
                _log.info(f"Teardown - Finish NFS folder deletion")

            else:
                raise NotADirectoryError(
                    f"Failed to delete directory because it doesnt exists: [{config.NFS_ROOT_DIR_DEST}]"
                )
        else:
            raise ValueError(f"Illegal environment value type: {config.TEST_ENV}")
    if config.CLEAN_UP and config.DEBUG_MODE_LOCAL:
        for p in ValueStorage.discrete_list:
            cleanup_env(p["product_id"], p["product_version"], initial_mapproxy_config)


if config.DEBUG_MODE_LOCAL:
    config.PVC_UPDATE_ZOOM = True
    config.MAX_ZOOM_TO_CHANGE = 4

if config.RUN_IT:
    test_manual_discrete_ingest()
    test_watch_discrete_ingest()
