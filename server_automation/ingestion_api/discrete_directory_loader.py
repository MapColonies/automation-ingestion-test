"""This module responsible interface with orig upload directory"""
import logging
import os
from mc_automation_tools import shape_convertor as sv
from server_automation.configuration import config
_log = logging.getLogger('server_automation.ingestion_api.discrete_directory_loader')


def validate_source_directory(path):
    """This module validate source directory is valid for ingestion process"""
    if not os.path.exists(path):
        _log.error(f'Path [{path}] not exists')
        return False, f'Path [{path}] not exists'

    if not os.path.exists(os.path.join(path,config.SHAPES_PATH)):
        _log.error(f'Path [{os.path.join(path,config.SHAPES_PATH)}] not exists')
        return False, f'Path [{os.path.join(path, config.SHAPES_PATH)}] not exists'

    if not os.path.exists(os.path.join(path, config.TIFF_PATH)):
        _log.error(f'Path [{os.path.join(path, config.TIFF_PATH)}] not exists')
        return False, f'Path [{os.path.join(path, config.TIFF_PATH)}] not exists'

    res = set(config.SHAPE_FILE_LIST).intersection(os.listdir(os.path.join(path, config.SHAPES_PATH)))
    if len(res) != len(config.SHAPE_FILE_LIST):
        _log.error(f'Path [{os.path.join(path, config.SHAPES_PATH)}] missing files:\n'
                   f'{set(config.SHAPE_FILE_LIST).symmetric_difference(set(config.SHAPE_FILE_LIST).intersection(os.listdir(os.path.join(path, config.SHAPES_PATH))))}')
        return False, f'Path [{os.path.join(path, config.SHAPES_PATH)}] missing files:{set(config.SHAPE_FILE_LIST).symmetric_difference(set(config.SHAPE_FILE_LIST).intersection(os.listdir(os.path.join(path, config.SHAPES_PATH))))}'


    shape_metadata_shp = sv.shp_to_geojson(os.path.join(path, config.SHAPES_PATH, 'ShapeMetadata.shp'))
    Product_shp = sv.shp_to_geojson(os.path.join(path, config.SHAPES_PATH, 'Product.shp'))
    Files_shp = sv.shp_to_geojson(os.path.join(path, config.SHAPES_PATH, 'Files.shp'))
    img_path = os.path.join(path, config.TIFF_PATH)
    res = sv.generate_oversear_request(shape_metadata_shp, Product_shp, Files_shp, img_path)

    return True, res
