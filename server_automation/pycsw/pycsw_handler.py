"""This module provide multiple pycsw client requests"""
import json
from server_automation.configuration import config
from mc_automation_tools import base_requests


def get_raster_records(host=config.PYCSW_URL, params=config.PYCSW_GET_RECORD_PARAMS):
    """
    This function will return all records of raster's data
    :param host: pycsw server's entrypoiny url
    :param params: request parameters for GetRecords API request with json result
    :return: Dict -> list of records - json format
    """
    records_list = []
    next_record = -1
    try:
        while next_record:
            resp = base_requests.send_get_request(host, params)
            s_code = resp.status_code
            msg = resp.content
            if s_code != config.ResponseCode.Ok.value:
                raise Exception(f'Failed on request GetRecords with error:[{str(msg)}] and status code: [{str(s_code)}]')
            records = json.loads(msg)
            cuurent_records = records['csw:GetRecordsResponse']['csw:SearchResults']['mcraster:MCRasterRecord']
            params['startPosition'] = records['csw:GetRecordsResponse']['csw:SearchResults']['@nextRecord']
            next_record = int(records['csw:GetRecordsResponse']['csw:SearchResults']['@nextRecord'])
            records_list = records_list + cuurent_records

    except Exception as e:
        raise Exception(f'Failed on request records on pycsw host:[{host}] with error:{str(e)}')
    del params['startPosition']
    return records_list


def get_record_by_id(product_name, product_id, host=config.PYCSW_URL, params=config.PYCSW_GET_RECORD_PARAMS):
    """
    This method find record by semi unique ID -> product_name & product_id
    :param product_name: discrete name
    :param product_id: discrete version
    :param host: pycsw server's entrypoiny url
    :param params: request parameters for GetRecords API request with json result
    :return: list of records [orthophoto and orthophotoHistory]
    """
    res = get_raster_records(host, params)
    records_list = [record for record in res if (record['mcraster:productId'] == product_name and record['mcraster:productVersion'] == product_id)]
    return records_list