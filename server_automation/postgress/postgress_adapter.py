import logging
from server_automation.configuration import config
from mc_automation_tools import postgres

_log = logging.getLogger("server_automation.postgress.postgress_adapter")


def get_current_job_id(product_id, product_version, db_name=config.PG_JOB_TASK_DB_NAME):
    """This method query and return uuid of current ingestion job according keys: productId and productVersion"""
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    keys_values = {"resourceId": product_id, "version": product_version}
    res = client.get_rows_by_keys(
        "Job", keys_values, order_key="creationTime", order_desc=True
    )
    latest_job_id = res[0][0]
    _log.info(f"Received current job id: [{latest_job_id}], from date: {res[0][6]}")
    return latest_job_id


def get_job_by_id(job_id, db_name=config.PG_JOB_TASK_DB_NAME):
    """This  method will provide job full row data from db, by jobid"""
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    res = client.get_rows_by_keys("Job", {"id": job_id}, return_as_dict=True)
    return res[0]


def get_tasks_by_job(job_id, db_name=config.PG_JOB_TASK_DB_NAME):
    """
    This method query the db and return all related task to the current job_id
    :return:
    """
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    res = client.get_rows_by_keys("Task", {"jobId": job_id}, return_as_dict=True)
    return res


def clean_layer_history(job_id, db_name=config.PG_AGENT):
    """This will directly clean job and related task from db"""
    deletion_command = f"""DELETE FROM "layer_history" WHERE "layerId"='{job_id}';"""
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    try:
        client.command_execute([deletion_command])
        _log.info(
            f"Cleaned up successfully (layer_history) - from [{config.PG_AGENT}] , job: [{job_id}]"
        )
        return {"status": "OK", "message": f"deleted ok {job_id}"}

    except Exception as e:
        return {"status": "Failed", "message": f"deleted Failed: [{str(e)}]"}


def clean_job_task(job_id, db_name=config.PG_JOB_TASK_DB_NAME):
    """This will directly clean job and related task from db"""
    deletion_command = f"""DELETE FROM "Task" WHERE "jobId"='{job_id}';DELETE FROM "Job" WHERE "id"='{job_id}';"""
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    try:
        client.command_execute([deletion_command])
        _log.info(
            f"Cleaned up successfully (job + task)- [{config.PG_JOB_TASK_DB_NAME}] job: [{job_id}]"
        )
        return {"status": "OK", "message": f"deleted ok {job_id}"}

    except Exception as e:
        return {"status": "Failed", "message": f"deleted Failed: [{str(e)}]"}


def clean_pycsw_record(product_id, db_name=config.PG_RECORD_PYCSW_DB):
    """This will directly clean job and related task from db"""
    deletion_command = f"""DELETE FROM "records" WHERE "product_id"='{product_id}'"""
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    try:
        client.command_execute([deletion_command])
        _log.info(
            f"Cleaned up successfully (record pycsw) - from [{config.PG_RECORD_PYCSW_DB}] , records: [{product_id}]"
        )
        return {"status": "OK", "message": f"deleted ok {product_id}"}

    except Exception as e:
        return {"status": "Failed", "message": f"deleted Failed: [{str(e)}]"}


def get_mapproxy_config(db_name=config.PG_MAPPROXY_CONFIG):
    """will get mapproxy-config data"""
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)

    try:
        res = client.get_column_by_name(table_name="config", column_name="data")[0]
        _log.info(f"got json-config ok")
        return {"status": "OK", "message": res}

    except Exception as e:
        return {"status": "Failed", "message": f"Failed get json-config: [{str(e)}]"}


def get_mapproxy_configs(table_name="config", db_name=config.PG_MAPPROXY_CONFIG):
    """This method query and return uuid of current ingestion job according keys: productId and productVersion"""

    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=int(config.PG_PORT))
    res = client.get_rows_by_order(
        table_name=table_name,
        order_key="updated_time",
        order_desc=True,
        return_as_dict=True,
    )
    _log.info(f"Received {len(res)} of mapproxy config files")
    return res


def delete_config_mapproxy(
        id, value, db_name=config.PG_MAPPROXY_CONFIG, table_name="config"
):
    """
    This method will delete entire row on mapproxy
    :param id: id of specific configuration
    :param value: value of id
    :param db_name: name of db
    :param table_name: name of table
    """
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    res = client.delete_row_by_id(table_name, id, value)


def delete_pycsw_record(
        product_id, value, db_name=config.PG_RECORD_PYCSW_DB, table_name="records"
):
    """
    This method will delete entire row on mapproxy
    :param product_id: id of layer as product_id
    :param value: The product_id
    :param db_name: name of db
    :param table_name: name of table
    """
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    res = client.delete_row_by_id(table_name, product_id, value)


def delete_agent_path(
        layer_id, value, db_name=config.PG_AGENT, table_name="layer_history"
):
    """
    This method will delete entire row on mapproxy
    :param layer_id: represent the later unique ID
    :param value: value of id
    :param db_name: name of db
    :param table_name: name of table
    """
    client = postgres.PGClass(config.PG_HOST, db_name, config.PG_USER, config.PG_PASS,port=6432)
    res = client.delete_row_by_id(table_name, layer_id, value)
