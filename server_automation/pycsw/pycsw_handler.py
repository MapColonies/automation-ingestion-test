"""This module provide multiple pycsw client requests"""
import xmltodict
from mc_automation_tools import base_requests

from server_automation.configuration import config

CSW_SEARCH_RESULTS = "csw:SearchResults"

CSW_GET_RECORDS_RESPONSE = "csw:GetRecordsResponse"


def get_raster_records(
    host=config.PYCSW_URL, params=config.PYCSW_GET_RECORD_PARAMS
):
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
            resp = base_requests.send_get_request(
                host, params, header=config.HEADERS_FOR_MAPPROXY
            )
            s_code = resp.status_code
            if s_code != config.ResponseCode.Ok.value:
                raise RuntimeError(
                    f"Failed on request GetRecords with error:[{str(resp.text)}] and status code: [{str(s_code)}]"
                )

            records = xmltodict.parse(resp.content)
            cuurent_records = records[CSW_GET_RECORDS_RESPONSE][
                CSW_SEARCH_RESULTS
            ]["mc:MCRasterRecord"]
            params["startPosition"] = records[CSW_GET_RECORDS_RESPONSE][
                CSW_SEARCH_RESULTS
            ]["@nextRecord"]
            next_record = int(
                records[CSW_GET_RECORDS_RESPONSE][CSW_SEARCH_RESULTS][
                    "@nextRecord"
                ]
            )
            records_list = records_list + cuurent_records

    except Exception as e:
        raise RuntimeError(
            f"Failed on request records on pycsw host:[{host}] with error:{str(e)}"
        )
    del params["startPosition"]
    return records_list


def get_record_by_id(
    product_name,
    product_id,
    host=config.PYCSW_URL,
    params=config.PYCSW_GET_RECORD_PARAMS,
):
    """
    This method find record by semi unique ID -> product_name & product_id
    :param product_name: discrete name
    :param product_id: discrete version
    :param host: pycsw server's entrypoiny url
    :param params: request parameters for GetRecords API request with json result
    :return: list of records [orthophoto and orthophotoHistory]
    """
    res = get_raster_records(host, params)
    records_list = [
        record
        for record in res
        if (
            record["mc:productId"] == product_name
            and record["mc:productVersion"] == product_id
        )
    ]
    return records_list
