# pylint: disable=line-too-long, invalid-name, fixme
"""This module provide test full functionality """
import logging
import time
from server_automation.configuration import config
from server_automation.ingestion_api import discrete_agent_api
from server_automation.postgress import postgress_adapter
from mc_automation_tools import common as common
from mc_automation_tools import s3storage as s3
_log = logging.getLogger('server_automation.function.executors')


def start_manuel_ingestion(path):
    """This method will trigger new process of discrete ingestion by provided path"""
    _log.info(f'Send ingestion request for dir: {path}')
    resp = discrete_agent_api.post_manual_trigger(path)
    status_code = resp.status_code
    content = resp.text
    _log.info(f'receive from agent - manual: status code [{status_code}] and message: [{content}]')
    return status_code, content


def follow_running_task(job_id, timeout=config.FOLLOW_TIMEOUT):
    """This method will follow running ingestion task and return results on finish"""

    t_end = time.time() + timeout
    running = True
    while running:
        job = postgress_adapter.get_job_by_id(job_id, db_name=config.PG_JOB_TASK_DB_NAME)
        status = job['status']
        if status == config.JobStatus.Completed.value:

            return {'status': status, 'message': 'OK'}
        else:
            print('temp = on progress')
