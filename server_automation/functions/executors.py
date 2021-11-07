# pylint: disable=line-too-long, invalid-name, fixme
"""This module provide test full functionality """
import logging
import time
import json
import glob
import os
from shapely.geometry import Polygon
from server_automation.configuration import config
from server_automation.ingestion_api import discrete_agent_api, discrete_directory_loader, azure_pvc_api
from server_automation.postgress import postgress_adapter
from server_automation.graphql import gql_wrapper
from server_automation.pycsw import pycsw_handler

from discrete_kit.validator.json_compare_pycsw import *

from mc_automation_tools import common as common
from mc_automation_tools import shape_convertor, base_requests
from mc_automation_tools import s3storage as s3
from discrete_kit.functions import metadata_convertor

_log = logging.getLogger('server_automation.function.executors')


def stop_watch():
    """
    This method stop and validate stop / status api of agent for watching
    :return: result dict: {state: bool, reason: str}
    """
    try:
        resp = discrete_agent_api.post_stop_watch()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {'state': False, 'reason': f'Failed on getting watch status API: [{status_code}]:[{resp.content}]'}

        reason = json.loads(resp.content)
        if reason['isWatching']:
            return {'state': False, 'reason': f'Failed on stop watch via status API: [{json.loads(resp.content)}]'}
        resp = discrete_agent_api.get_watching_statuses()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {'state': False,
                    'reason': f'Failed on getting watch status API after changing: [{status_code}]:[{resp.content}]'}

        return {'state': True, 'reason': 'isWatch=False - agent not watching'}
    except Exception as e:
        _log.error(f'Failed on stop watching process with error: [{str(e)}]')
        raise Exception(f'Failed on stop watching process with error: [{str(e)}]')


def start_watch():
    """
    This method start and validate start \ status api of agent for watching
    :return: result dict: {state: bool, reason: str}
    """
    try:
        resp = discrete_agent_api.post_start_watch()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {'state': False,
                    'reason': f'Failed on getting watch status API: [{status_code}]:[{resp.content}]'}

        reason = json.loads(resp.content)
        if not reason['isWatching']:
            return {'state': False, 'reason': f'Failed on start watch via status API: [{resp.content}]'}
        resp = discrete_agent_api.get_watching_statuses()
        status_code = resp.status_code
        if status_code != config.ResponseCode.Ok.value:
            return {'state': False,
                    'reason': f'Failed on getting watch status API after changing: [{status_code}]:[{resp.content}]'}

        return {'state': True, 'reason': 'isWatch=True - agent on watching'}

    except Exception as e:
        _log.error(f'Failed on start watching process with error: [{str(e)}]')
        raise Exception(f'Failed on start watching process with error: [{str(e)}]')


def init_watch_ingestion_src(env=config.EnvironmentTypes.QA.name):
    """
    This method create test dedicated folder of source discrete for ingestion
    :param env:
    :return:
    """

    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
        host = config.PVC_HANDLER_ROUTE
        api = config.PVC_WATCH_CREATE_DIR
        change_api = config.PVC_WATCH_UPDATE_SHAPE
        res = init_ingestion_src_pvc(host, api, change_api, update_tfw_url=config.PVC_CHANGE_WATCH_MAX_ZOOM)
        return res
    elif env == config.EnvironmentTypes.PROD.name:
        src = os.path.join(config.NFS_WATCH_ROOT_DIR, config.NFS_WATCH_SOURCE_DIR)
        dst = os.path.join(config.NFS_WATCH_ROOT_DIR, config.NFS_WATCH_ROOT_DIR, config.NFS_WATCH_DEST_DIR,
                           common.generate_uuid())
        res = init_ingestion_src_fs(src, dst, watch=True)
        return res
    else:
        raise Exception(f'Illegal environment value type: {env}')


def init_ingestion_src(env=config.EnvironmentTypes.QA.name):
    """
    This module will init new ingestion source folder.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
        res = init_ingestion_src_pvc()
        return res
    elif env == config.EnvironmentTypes.PROD.name:
        src = os.path.join(config.NFS_ROOT_DIR, config.NFS_SOURCE_DIR)
        dst = os.path.join(config.NFS_ROOT_DIR, config.NFS_DEST_DIR)
        try:
            res = init_ingestion_src_fs(src, dst)
            return res
        except FileNotFoundError as e:
            raise e
        except Exception as e1:
            raise Exception(f'Failed generating testing directory with error: {str(e1)}')

    else:
        raise ValueError(f'Illegal environment value type: {env}')


def init_ingestion_src_fs(src, dst, watch=False):
    """
        This module will init new ingestion source folder - for file system / NFS deployment.
        The prerequisites must have source folder with suitable data and destination folder for new data
        The method will duplicate and rename metadata shape file to unique running name
        :return:dict with ingestion_dir and resource_name
    """
    if watch:
        deletion_watch_dir = os.path.dirname(dst)
        if os.path.exists(deletion_watch_dir):
            command = f'rm -rf {deletion_watch_dir}/*'
            os.system(command)
    else:
        deletion_watch_dir = dst
        if os.path.exists(dst):
            command = f'rm -rf {deletion_watch_dir}'
            os.system(command)

    if not os.path.exists(src):
        raise FileNotFoundError(f'[{src}] directory not found')

    try:
        command = f'cp -r {src}/. {dst}'
        os.system(command)
        if os.path.exists(dst):
            _log.info(f'Success copy and creation of test data on: {dst}')
        else:
            raise IOError('Failed on creating ingestion directory')

    except Exception as e2:
        _log.error(f'Failed copy files from {src} into {dst} with error: [{str(e2)}]')
        raise e2

    try:
        file = os.path.join(dst, config.SHAPES_PATH, config.SHAPE_METADATA_FILE)
        source_name = update_shape_fs(file)
        _log.info(
            f'[{file}]:was changed resource name: {source_name}')
    except Exception as e:
        _log.error(f'Failed on updating shape file: {file} with error: {str(e)}')
        raise e

    if config.PVC_UPDATE_ZOOM:
        res = metadata_convertor.replace_discrete_resolution(dst,
                                                             str(config.zoom_level_dict[config.MAX_ZOOM_TO_CHANGE]),
                                                             'tfw')

    return {'ingestion_dir': dst, 'resource_name': source_name, 'max_resolution': res}


def init_ingestion_src_pvc(host=config.PVC_HANDLER_ROUTE, create_api=config.PVC_CLONE_SOURCE,
                           change_api=config.PVC_CHANGE_METADATA, update_tfw_url=config.PVC_CHANGE_MAX_ZOOM):
    """
    This module will init new ingestion source folder inside pvc - only on azure.
    The prerequisites must have source folder with suitable data and destination folder for new data
    The method will duplicate and rename metadata shape file to unique running name
    :return:dict with ingestion_dir and resource_name
    """
    try:
        resp = azure_pvc_api.create_new_ingestion_dir(host, create_api)
        if not resp.status_code == config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'Failed access pvc on source data cloning with error: [{resp.text}] and status: [{resp.status_code}]')
        msg = json.loads(resp.text)
        new_dir = msg['newDesination']
        _log.info(
            f'[{resp.status_code}]: New test running directory was created from source data: {msg["source"]} into {msg["newDesination"]}')
    except Exception as e:
        raise Exception(f'Failed access pvc on source data cloning with error: [{str(e)}]')

    try:
        resp = azure_pvc_api.make_unique_shapedata(host=host, api=change_api)
        if not resp.status_code == config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'Failed access pvc on source data updating metadata.shp with error: [{resp.text}] and status: [{resp.status_code}]')
        resource_name = json.loads(resp.text)['source']
        _log.info(
            f'[{resp.status_code}]: metadata.shp was changed resource name: {resource_name}')

    except Exception as e:
        raise Exception(f'Failed access pvc on changing shape metadata: [{str(e)}]')

    if config.PVC_UPDATE_ZOOM:
        try:
            resp = azure_pvc_api.change_max_zoom_tfw(host=host, api=update_tfw_url)
            if resp.status_code == config.ResponseCode.Ok.value:
                _log.info(f'Max resolution changed successfully: [{json.loads(resp.text)["json_data"][0]["reason"]}]')
            else:
                raise Exception(
                    f'Failed on updating zoom level with error: [{json.loads(resp.text)["message"]} | {json.loads(resp.text)["json_data"]}]')
        except Exception as e:
            raise IOError(f'Failed updating zoom max level with error: [{str(e)}]')
    return {'ingestion_dir': new_dir, 'resource_name': resource_name}


def validate_source_directory(path=None, env=config.EnvironmentTypes.QA.name, watch=False):
    """
    This will validate that source directory include all needed files for ingestion
    :param path: None if working on azure - qa \ dev with pvc
    :param env: default qa for azure running with pvc
    :return: True \ False + response json
    """

    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
        if watch:
            resp = azure_pvc_api.validate_ingestion_directory(api=config.PVC_WATCH_VALIDATE)
        else:
            resp = azure_pvc_api.validate_ingestion_directory()
        content = json.loads(resp.text)
        if content.get('json_data'):
            validation_tiff_dict, error_msg = validate_tiff_exists(path, content.get('json_data')['fileNames'])
            assert all(validation_tiff_dict.values()) is True, f' Failed: on following ingestion process [{error_msg}]'
            return not content['failure'], content['json_data']

        else:
            return not content['failure'], content['message']
    elif env == config.EnvironmentTypes.PROD.name:
        state, resp = discrete_directory_loader.validate_source_directory(path)
        return state, resp
    else:
        raise Exception(f'illegal Environment name: [{env}]')


def start_manual_ingestion(path, env=config.EnvironmentTypes.QA.name):
    """This method will trigger new process of discrete ingestion by provided path"""
    # validate directory include all needed files and data
    source_ok, body = validate_source_directory(path, env)
    if not source_ok:
        raise FileNotFoundError(f'Directory [{path}] with missing files / errors msg: [{body}]')

    _log.info(f'Send ingestion request for dir: {path}')
    if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
        relative_path = path.split(config.PVC_ROOT_DIR)[1]
    elif env == config.EnvironmentTypes.PROD.name:
        relative_path = config.NFS_DEST_DIR

    resp = discrete_agent_api.post_manual_trigger(relative_path)
    status_code = resp.status_code
    content = resp.text
    _log.info(f'receive from agent - manual: status code [{status_code}] and message: [{content}]')

    return status_code, content, body


def start_watch_ingestion(path, env=config.EnvironmentTypes.QA.name):
    """This method will start watch agent and validate start of current job"""

    # validate directory include all needed files and data
    source_ok, body = validate_source_directory(path, env, watch=True)
    if not source_ok:
        raise FileNotFoundError(f'Directory [{path}] with missing files / errors msg: [{body}]')

    _log.info(f'Init ingestion via watch start request for dir: {path}')
    # if env == config.EnvironmentTypes.QA.name or env == config.EnvironmentTypes.DEV.name:
    #     relative_path = path.split(config.PVC_ROOT_DIR)[1]
    # elif env == config.EnvironmentTypes.PROD.name:
    #     relative_path = config.NFS_DEST_DIR

    resp = start_watch()
    watch_state = resp['state']
    if not watch_state:
        raise Exception(f'Failed on start watching with error:\n'
                        f'{resp["reason"]}')

    _log.info(f'Receive from agent - watch status: [{watch_state}] and message: [{resp["reason"]}]')

    return watch_state, resp["reason"], body


def follow_running_task(product_id, product_version, timeout=config.FOLLOW_TIMEOUT):
    """This method will follow running ingestion task and return results on finish"""

    t_end = time.time() + timeout
    running = True
    resp = gql_wrapper.get_job_by_product(product_id, product_version, host=config.GQK_URL)
    _log.info(resp)
    if not resp:
        raise Exception(f'Job for {product_id}:{product_version} not found')

    while running:
        time.sleep(config.SYSTEM_DELAY // 4)
        job = gql_wrapper.get_job_by_product(product_id, product_version, host=config.GQK_URL)

        job_id = job['id']

        status = job['status']
        reason = job['reason']
        tasks = job['tasks']

        completed_task = sum(1 for task in tasks if task['status'] == config.JobStatus.Completed.name)
        _log.info(f'\nIngestion status of job for resource: {product_id}:{product_version} is [{status}]\n'
                  f'finished tasks for current job: {completed_task} / {len(tasks)}')

        if status == config.JobStatus.Completed.name:
            return {'status': status, 'message': " ".join(['OK', reason]), 'job_id': job_id}
        elif status == config.JobStatus.Failed.name:
            return {'status': status, 'message': " ".join(['Failed: ', reason]), 'job_id': job_id}

        current_time = time.time()

        if t_end < current_time:
            return {'status': status, 'message': " ".join(['Failed: ', 'got timeout while following job running']),
                    'job_id': job_id}


def update_shape_fs(shp):
    current_time_str = common.generate_datatime_zulu().replace('-', '_').replace(':', '_')
    resp = shape_convertor.add_ext_source_name(shp, current_time_str)
    return resp


def validate_tiff_exists(path_name, tiff_list):
    # path_name = '/tmp/ingestion/watch/test_data_automation/89b89916-dd38-44fb-8a86-a1ab2b606cd6'
    # tiff_list = ['/X185_Y167.tiff']
    err = ''
    x = {}
    text_files = glob.glob(path_name + "/**/*.tif", recursive=True)
    for item in tiff_list:
        if '.' in item:
            item = item.split('.')[0]
        if any(item in text for text in text_files):
            x[item] = True
        else:
            x[item] = False
            err = 'tiff files missing :' + item
    if len(text_files) != len(tiff_list):
        x['length_is_equal'] = False
        err = 'tiff files length is not equal'
    else:
        x['length_is_equal'] = True
    if err:
        return x, err
    else:
        return x, ""


def test_cleanup(product_id, product_version, initial_mapproxy_config):
    try:
        """This method will clean all created test data"""
        job_id = postgress_adapter.get_current_job_id(product_id, product_version)
        postgress_adapter.clean_job_task(job_id)
        s3_conn = s3.S3Client(config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY)
        s3_conn.delete_folder(config.S3_BUCKET_NAME, product_id)
        current_config_mapproxy = postgress_adapter.get_mapproxy_configs(table_name='config',
                                                                         db_name=config.PG_MAPPROXY_CONFIG)
        postgress_adapter.clean_pycsw_record(product_id)
        if len(current_config_mapproxy) > len(initial_mapproxy_config):
            postgress_adapter.delete_config_mapproxy('id', current_config_mapproxy[0]['id'])
        postgress_adapter.delete_agent_path("layerId", product_id)
        postgress_adapter.delete_pycsw_record('product_id', product_id)

        _log.info(f'Cleanup was executed and delete at end of test:\n'
                  f'DB - job and related task\n'
                  f'DB - mapproxy-config\n'
                  f'DB - pycsw-records\n'
                  f'DB - agent-discrete\n'
                  f'S3 - uploaded layers\n')

    except Exception as e:
        _log.error(f'Failed on cleanup with error: {str(e)}')


def validate_pycsw2(source_json_metadata, product_id=None, product_version=None):
    # todo -> implement full function
    """
    :return: dict of result validation
    """
    res_dict = {'validation': True, 'reason': ""}
    pycsw_records = pycsw_handler.get_record_by_id(product_id, product_version, host=config.PYCSW_URL,
                                                   params=config.PYCSW_GET_RECORD_PARAMS)

    if not pycsw_records:
        return {'validation': False, 'reason': f'Records of [{product_id}] not found'}
    links = {}
    for record in pycsw_records:
        links[record['mc:productType']] = {
            record['mc:links'][0]['@scheme']: record['mc:links'][0]['#text'],
            record['mc:links'][1]['@scheme']: record['mc:links'][1]['#text'],
            record['mc:links'][2]['@scheme']: record['mc:links'][2]['#text']
        }
    validation_flag, err_dict = validate_pycsw_with_shape_json(pycsw_records, source_json_metadata)
    res_dict['validation'] = validation_flag
    res_dict['reason'] = err_dict
    return res_dict, pycsw_records, links


def validate_pycsw(gqk=config.GQK_URL, product_id=None, source_data=None):
    """
    :return: dict of result validation
    """
    # Todo -> refactoring records getting with Danny's validator
    pycsw_record = pycsw_handler.get_record_by_id(source_data, product_id, host=config.PYCSW_URL,
                                                  params=config.PYCSW_GET_RECORD_PARAMS)

    # TODO -> this is old records getting by pycsw -> should stay as mark on code and use the new getting directly from pycsw
    res_dict = {'validation': True, 'reason': ""}
    # pycsw_record = gql_wrapper.get_pycsw_record(host=gqk, product_id=product_id)
    if not pycsw_record['data']['search']:
        return {'validation': False, 'reason': f'Record of [{product_id}] not found'}

    # generate dict of protocol:related url
    links = {
        pycsw_record['data']['search'][0]['links'][0]['protocol']: pycsw_record['data']['search'][0]['links'][0]['url'],
        pycsw_record['data']['search'][0]['links'][1]['protocol']: pycsw_record['data']['search'][0]['links'][1]['url'],
        pycsw_record['data']['search'][0]['links'][2]['protocol']: pycsw_record['data']['search'][0]['links'][2]['url']}

    WMS_STATE = base_requests.send_get_request(links['WMS']).status_code == config.ResponseCode.Ok.value
    WMTS_STATE = base_requests.send_get_request(links['WMTS']).status_code == config.ResponseCode.Ok.value

    if not WMS_STATE and not WMTS_STATE:
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'], f'\nProtocol urls that provided not correct: {links}'])

    # validate product id:
    record_product_id = pycsw_record['data']['search'][0]['productId']
    orig_product_id = source_data['metadata']['productId']
    if record_product_id != orig_product_id:
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'], f'\nWrong product id: orig:[{orig_product_id}] != pycsw_record:[{record_product_id}]'])

    # validate product name:
    record_product_Name = pycsw_record['data']['search'][0]['productName']
    orig_product_Name = source_data['metadata']['productName']
    if record_product_Name != orig_product_Name:
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'],
             f'\nWrong product name: orig name:[{orig_product_Name}] != pycsw_record name:[{record_product_Name}]'])

    # validate description:
    record_description = pycsw_record['data']['search'][0]['description']
    orig_description = source_data['metadata']['description']
    if record_description != orig_description:
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'],
             f'\nWrong description: orig description:[{orig_description}] != pycsw_record description:[{record_description}]'])

    # validate sensor type:
    record_sensor = pycsw_record['data']['search'][0]['sensorType']
    orig_sensor = source_data['metadata']['sensorType']
    if orig_sensor != record_sensor:
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'],
             f'\nWrong sensor types: orig sensor types:[{orig_sensor}] != pycsw_record sensor types:[{record_sensor}]'])

    # validate accuracy:
    record_accuracy = str(pycsw_record['data']['search'][0]['accuracyCE90'])
    orig_accuracy = str(source_data['metadata']['accuracyCE90'])
    if orig_accuracy != record_accuracy:
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'],
             f'\nWrong accuracy: orig accuracy:[{orig_accuracy}] != pycsw_record accuracy:[{record_accuracy}]'])

    # validate geometry:
    record_geometry = pycsw_record['data']['search'][0]['footprint']['coordinates'][0]
    orig_geometry = source_data['metadata']['footprint']['coordinates'][0]
    poly_record = Polygon(record_geometry)
    poly_orig = Polygon(orig_geometry)

    if not poly_record.equals(poly_orig):
        res_dict['validation'] = False
        res_dict['reason'] = "\n----------------------".join(
            [res_dict['reason'],
             f'\nWrong geometry: orig geometry:[{orig_geometry}] != pycsw_record geometry:[{record_geometry}]'])

    return res_dict, pycsw_record


def validate_new_discrete(pycsw_records, product_id, product_version):
    """
    This method will validate access and data on mapproxy
    :return:
    """

    links = {}
    for record in pycsw_records:
        links[record['mc:productType']] = {
            record['mc:links'][0]['@scheme']: record['mc:links'][0]['#text'],
            record['mc:links'][1]['@scheme']: record['mc:links'][1]['#text'],
            record['mc:links'][2]['@scheme']: record['mc:links'][2]['#text']
        }

    results = dict.fromkeys(list(links.keys()), dict())
    for link_group in list(links.keys()):
        results[link_group] = {k: v for k, v in links[link_group].items()}

    for group in results.keys():
        if group == 'Orthophoto':
            layer_name = "-".join([product_id, group])
        elif group == 'OrthophotoHistory':
            layer_name = "-".join([product_id, product_version, group])  # layer name
        else:
            raise ValueError(f'records type on recognize as OrthophotoHistory or Orthophoto')

        results[group]['is_valid'] = {}
        # check that wms include the new layer on capabilities
        wms_capabilities = common.get_xml_as_dict(results[group]['WMS'])
        results[group]['is_valid']['WMS'] = layer_name in [layer['Name'] for layer in
                                                           wms_capabilities['WMS_Capabilities']['Capability']['Layer'][
                                                               'Layer']]

        # check that wmts include the new layer on capabilities
        wmts_capabilities = common.get_xml_as_dict(results[group]['WMTS'])
        results[group]['is_valid']['WMTS'] = layer_name in [layer['ows:Identifier'] for layer in
                                                            wmts_capabilities['Capabilities']['Contents']['Layer']]
        wmts_layer_properties = [layer for layer in wmts_capabilities['Capabilities']['Contents']['Layer'] if
                                 layer_name in layer['ows:Identifier']]

        # check access to random tile by wmts_layer url
        if config.TEST_ENV == config.EnvironmentTypes.QA.name or config.TEST_ENV == config.EnvironmentTypes.DEV.name:
            s3_conn = s3.S3Client(config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY)
            list_of_tiles = s3_conn.list_folder_content(config.S3_BUCKET_NAME, "/".join([product_id, product_version]))
        elif config.TEST_ENV == config.EnvironmentTypes.PROD.name:
            path = os.path.join(config.NFS_TILES_DIR, product_id, product_version)
            list_of_tiles = []
            # r=root, d=directories, f = files
            for r, d, f in os.walk(path):
                for file in f:
                    if '.png' in file:
                        list_of_tiles.append(os.path.join(r, file))
        else:
            raise Exception(f'Illegal environment value type: {config.TEST_ENV}')

        zxy = list_of_tiles[len(list_of_tiles) - 1].split('/')[-3:]
        zxy[2] = zxy[2].split('.')[0]
        tile_matrix_set = wmts_layer_properties[0]['TileMatrixSetLink']['TileMatrixSet']
        wmts_layers_url = results[group]['WMTS_LAYER']
        wmts_layers_url = wmts_layers_url.format(TileMatrixSet=tile_matrix_set, TileMatrix=zxy[0], TileCol=zxy[1],
                                                 TileRow=zxy[2])  # formatted url for testing
        resp = base_requests.send_get_request(wmts_layers_url)
        results[group]['is_valid']['WMTS_LAYER'] = resp.status_code == config.ResponseCode.Ok.value

    # validation iteration -> check if all URL's state is True
    validation = True
    for group_name, value in results.items():
        if not all(val for key, val in value['is_valid'].items()):
            validation = False
            break
    return {'validation': validation, 'reason': results}


def get_json_schema(path_to_schema):
    """This function loads the given schema available"""
    try:
        with open(path_to_schema, 'r') as file:
            schema = json.load(file)
    except IOError:
        return None
    return schema


def get_folder_path_by_name(path, name):
    p_walker = [x[0] for x in os.walk(path)]
    path = ("\n".join(s for s in p_walker if name.lower() in s.lower()))
    return path
