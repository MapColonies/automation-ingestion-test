"""This module responsible interface with orig upload directory"""
import logging
import os
from pathlib import Path

from discrete_kit.configuration import config as cfg
from discrete_kit.functions.shape_functions import *
from discrete_kit.validator.schema_validator import *
from mc_automation_tools import shape_convertor as sv

from server_automation.configuration import config as a_config

_log = logging.getLogger("server_automation.ingestion_api.discrete_directory_loader")


#
# def validate_source_directory(path):
#     """This module validate source directory is valid for ingestion process"""
#     if not os.path.exists(path):
#         _log.error(f'Path [{path}] not exists')
#         return False, f'Path [{path}] not exists'
#
#     if not os.path.exists(os.path.join(path, config.SHAPES_PATH)):
#         _log.error(f'Path [{os.path.join(path,config.SHAPES_PATH)}] not exists')
#         return False, f'Path [{os.path.join(path, config.SHAPES_PATH)}] not exists'
#
#     if not os.path.exists(os.path.join(path, config.TIFF_PATH)):
#         _log.error(f'Path [{os.path.join(path, config.TIFF_PATH)}] not exists')
#         return False, f'Path [{os.path.join(path, config.TIFF_PATH)}] not exists'
#
#     res = set(config.SHAPE_FILE_LIST).intersection(os.listdir(os.path.join(path, config.SHAPES_PATH)))
#     if len(res) != len(config.SHAPE_FILE_LIST):
#         _log.error(f'Path [{os.path.join(path, config.SHAPES_PATH)}] missing files:\n'
#                    f'{set(config.SHAPE_FILE_LIST).symmetric_difference(set(config.SHAPE_FILE_LIST).intersection(os.listdir(os.path.join(path, config.SHAPES_PATH))))}')
#         return False, f'Path [{os.path.join(path, config.SHAPES_PATH)}] missing files:{set(config.SHAPE_FILE_LIST).symmetric_difference(set(config.SHAPE_FILE_LIST).intersection(os.listdir(os.path.join(path, config.SHAPES_PATH))))}'
#
#
#     shape_metadata_shp = sv.shp_to_geojson(os.path.join(path, config.SHAPES_PATH, 'ShapeMetadata.shp'))
#     Product_shp = sv.shp_to_geojson(os.path.join(path, config.SHAPES_PATH, 'Product.shp'))
#     Files_shp = sv.shp_to_geojson(os.path.join(path, config.SHAPES_PATH, 'Files.shp'))
#     img_path = os.path.join(path, config.TIFF_PATH)
#     res = sv.generate_oversear_request(shape_metadata_shp, Product_shp, Files_shp, img_path)
#
#     return True, res


def validate_source_directory(path):
    """This module validate source directory is valid for ingestion process"""
    missing_set_files = []
    if not os.path.exists(path):
        _log.error(f"Path [{path}] not exists")
        return False, f"Path [{path}] not exists"

    if not find_if_folder_exists(path, a_config.SHAPES_PATH):
        _log.error(f"Path [{os.path.join(path, a_config.SHAPES_PATH)}] not exists")
        return False, f"Path [{os.path.join(path, a_config.SHAPES_PATH)}] not exists"

    if not find_if_folder_exists(path, a_config.TIFF_PATH):
        _log.error(f"Path [{os.path.join(path, a_config.TIFF_PATH)}] not exists")
        return False, f"Path [{os.path.join(path, a_config.TIFF_PATH)}] not exists"

    ret_folder = get_folder_path_by_name(path, a_config.SHAPES_PATH)
    for file_name in cfg.files_names:
        for ext in cfg.files_extension_list:
            ret_extension_validation, missing = cfg.validate_ext_files_exists(
                os.path.join(ret_folder, file_name), ext
            )
            if not ret_extension_validation:
                missing_set_files.append(missing)
    if missing_set_files:
        return (
            False,
            f"Path [{os.path.join(path, a_config.SHAPES_PATH)}] missing files:{set(missing_set_files)}",
        )

    json_object_res = ShapeToJSON(ret_folder)
    # try:
    #     with open(Path(Path(__file__).resolve()).parent.parent / 'jsons/shape_file.json', 'w', encoding='utf-8') as f:
    #         json.dump(json.loads(json_object_res.get_json_output()), f, ensure_ascii=False)
    # except IOError:
    #     return False, "Cannot write json file to run validation on schema."

    # dir_name = os.path.dirname(__file__)
    # dir_name = Path(Path(dir_name).resolve()).parent
    # full_path = os.path.join(dir_name, discrete_kit.configuration.config.SCHEMA_FOLDER,
    #                          discrete_kit.configuration.config.JSON_NAME)
    # schema_file = open(full_path, 'r')
    # schema_data_to_comp = json.load(schema_file)
    # try:
    #     if validate_json_types(schema_data_to_comp,
    #                            json_object_res.get_json_output()) is None:
    #         return True, json_object_res.created_json
    # except Exception as e:
    #     return False, e
    return True, json_object_res.created_json
    # return True, res


def find_if_folder_exists(directory, folder_to_check):
    os.walk(directory)
    directory_lists = [x[0] for x in os.walk(directory)]
    for current_dir in directory_lists:
        if folder_to_check in current_dir:
            return True
    return False


def get_folder_path_by_name(path, name):
    p_walker = [x[0] for x in os.walk(path)]
    path = "\n".join(s for s in p_walker if name.lower() in s.lower())
    return path
