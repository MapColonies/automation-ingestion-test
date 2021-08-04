"""This module provide all method to access discrete ingestion bff service based on graphql"""
import logging
from server_automation.configuration import config
from mc_automation_tools import graphql

_log = logging.getLogger('automation_tools.graphql.gql_wrapper')





def get_jobs_task(host=config.GQK_URL):
    """return jobs data"""
    gql_client = graphql.GqlClient(host)
    res = gql_client.get_jobs_tasks()
    return res['data']['jobs']


def get_job_by_product(product_id, product_version, host=config.GQK_URL):
    all_jobs = get_jobs_task(host=config.GQK_URL)
    job = [element for element in all_jobs if element['resourceId'] == product_id and element['version'] == product_version]
    return job[0]


def get_pycsw_record(host, product_id):
    """
    This method query on pycsw catalog and get the record of specific layer
    :param host: gql endpoint
    :param product_id: id (source) of ingested layer
    :return: dict of record
    """
    try:
        gql_client = graphql.GqlClient(host)
        pycsw_template_request = config.PYCSW_QUERY_BY_PRODUCTID
        query = pycsw_template_request['query']
        variables = pycsw_template_request['variables']

        variables['opts']['filter'][1]['eq'] = product_id

        records = gql_client.execute_free_query(query, variables)


        # for record in records['data']['search']:
        #     if record.get('productId') == product_id:
        #         return record
        #
        #     # else:
        #     #     _log.error(f'Record not found on pycsw for product: [{product_id}]')

    except Exception as e:
        _log.error(f'Failed on getting pycsw record with error: [{str(e)}]')
        raise Exception(f'Failed on getting pycsw record with error: [{str(e)}]')

    return records
