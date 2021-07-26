"""This module will wrap access for azure's pv that raster ingestion based on - not for production testing"""
from server_automation.configuration import config
from mc_automation_tools import common
from mc_automation_tools import base_requests


def create_new_ingestion_dir(host=config.PVC_HANDLER_ROUTE, api=config.PVC_CLONE_SOURCE):
    """
    This method will send http get request to pvc server and create new directory of ingested source data
    :param host: route address to service
    :param api: routing dir
    :return: new directory on pv
    """
    url = common.combine_url(host, api)
    resp = base_requests.send_get_request(url)
    return resp


def make_unique_shapedata(host=config.PVC_HANDLER_ROUTE, api=config.PVC_CHANGE_METADATA):
    """
    This method will send http get request to pvc server and change shape metadata to unique running
    :param host: route address to service
    :param api: routing dir
    :return: new product name and id based on running time string generation
    """
    url = common.combine_url(host, api)
    resp = base_requests.send_get_request(url)
    return resp