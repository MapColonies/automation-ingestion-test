""" configuration for running ingestion tests"""
import json
from mc_automation_tools import common
from server_automation.models.structs import *


CONF_FILE = common.get_environment_variable("CONF_FILE", None)
if not CONF_FILE:
    raise EnvironmentError("Should provide path for CONF_FILE")
try:
    with open(CONF_FILE, "r", encoding="utf-8") as fp:
        conf = json.load(fp)
except Exception as e:
    raise EnvironmentError("Failed to load JSON for configuration") from e

_api_route = conf.get("api_routes")
########  general running environment ##########
environment = conf.get("environment")
# compatibility to azure + prod env
TEST_ENV = environment.get("name", EnvironmentTypes.QA.name)
SHAPES_PATH = environment.get("shapes_path_name", "Shapes")
TIFF_PATH = environment.get("tiff_path_name", "tiff")
SHAPE_METADATA_FILE = environment.get("shape_metadata_file_name", "ShapeMetadata.shp")
DEBUG_MODE_LOCAL = environment.get("debug", False)
# If should clean running data from env at the end
CLEAN_UP = environment.get("clean_up", False)
# if false -> will skip data validation scopes
VALIDATION_SWITCH = environment.get("validation_switch", True)
SYSTEM_DELAY = environment.get("system_delay", 60)
PROGRESS_TASK_DELAY = environment.get("progress_task_delay", 50)
FOLLOW_TIMEOUT = 60 * environment.get("follow_timeout", 5)

############################################  follow  ####################
_job_manager_params = conf.get("job_manager_params")
AMOUNT_OF_WORKERS = _job_manager_params.get("amount_of_workers", 1)
FOLLOW_JOB_BY_MANAGER = _job_manager_params.get("FOLLOW_JOB_BY_MANAGER", True)
JOB_MANAGER_URL = _job_manager_params.get("job_manager_url", None)

ORIG_DISCRETE_PATH = common.get_environment_variable(
    "ORIG_DISCRETE_PATH", "/home/ronenk1/dev/automation-server-test/shp/1"
)
SHAPE_FILE_LIST = [
    "Files.shp",
    "Files.dbf",
    "Product.shp",
    "Product.dbf",
    "ShapeMetadata.shp",
    "ShapeMetadata.dbf",
]
##########################################  Overseer params
_overseer_vars = conf.get('overseer_params')
OVERSEER_END_URL = _overseer_vars.get('overseer_end_point_url')
OVERSEER_JSON_LOCATION = _overseer_vars.get('geopackage_json')

##########################################  Ingestion API's sub urls & API
_ingestion_sub_url_api = conf.get("ingestion_sub_url_api")
INGESTION_MANUAL_TRIGGER = _ingestion_sub_url_api.get("ingestion_trigger", "trigger")
INGESTION_WATCHER_STATUS = _ingestion_sub_url_api.get(
    "ingestion_watch_status", "status"
)
INGESTION_START_WATCHER = _ingestion_sub_url_api.get("ingestion_start_watch", "start")
INGESTION_STOP_WATCHER = _ingestion_sub_url_api.get("ingestion_stop_watch", "stop")
INGESTION_AGENT_URL = _ingestion_sub_url_api.get("ingestion_agent_url", None)
################################################  MAPPROXY VARIABELS  ####
_mapproxy_vars = conf.get("mapproxy_variables")
WMS = _mapproxy_vars.get("wms")
WMTS = _mapproxy_vars.get("wmts")
WMTS_LAYER = _mapproxy_vars.get("wmts_layer")
###############################################  POSTGRESS CREDENTIALS  ##
_pg_credentials = conf.get("pg_credential")
PG_USER = _pg_credentials.get("pg_user", None)
PG_PASS = _pg_credentials.get("pg_pass", None)
PG_HOST = _pg_credentials.get("pg_host", None)
PG_JOB_TASK_DB_NAME = _pg_credentials.get("pg_job_task_table", None)
PG_RECORD_PYCSW_DB = _pg_credentials.get("pg_pycsw_record_table", None)
PG_MAPPROXY_CONFIG = _pg_credentials.get("pg_mapproxy_table", None)
PG_AGENT = _pg_credentials.get("pg_agent_table", None)
# PG_PYCSW_RECORD = common.get_environment_variable('PG_PYCSW_RECORD', None)


"""
#  NFS Directories  #
"""

_nfs_directories = conf.get("nfs_directories")
NFS_ROOT_DIR = _nfs_directories.get("nfs_root_directory", "/tmp")
NFS_ROOT_DIR_DEST = _nfs_directories.get("nfs_root_directory_destination", "/tmp")
NFS_SOURCE_DIR = _nfs_directories.get("nfs_source_directory", "ingestion/1")
NFS_DEST_DIR = _nfs_directories.get("nfs_destination_directory", "test_data")
NFS_TILES_DIR = _nfs_directories.get("nfs_tiles_directory", "/tmp")
NFS_WATCH_ROOT_DIR = _nfs_directories.get("nfs_watch_root_directory", "/tmp")
NFS_WATCH_SOURCE_DIR = _nfs_directories.get("nfs_watch_source_directory", "ingestion/1")
NFS_WATCH_BASE_DIR = _nfs_directories.get("nfs_watch_base_direcotry", "ingestion/1")
NFS_WATCH_DEST_DIR = _nfs_directories.get("nfs_watch_destination_directory", "watch")

"""
#  PVC ROUTES  #
"""

_pvc_routes = conf.get("pvc_routes")
PVC_CLONE_SOURCE = _pvc_routes.get("pvc_create_test_dir", "createTestDir")
PVC_CHANGE_METADATA = _pvc_routes.get("pvc_update_shape_metadata", "updateShape")
PVC_CHANGE_WATCH_METADATA = _pvc_routes.get(
    "pvc_update_watch_shape_metadata", "updateWatchShape"
)
PVC_VALIDATE_METADATA = _pvc_routes.get("pvc_validate_metadata", "validatePath")
PVC_DELETE_DIR = _pvc_routes.get("pvc_delete_directory", "deleteTestDir")
PVC_COPY_DIR = _pvc_routes.get("pvc_copy_file_to_src", "copyFile")
PVC_WATCH_CREATE_DIR = _pvc_routes.get("pvc_watch_create_directory", "createWatchDir")
PVC_WATCH_UPDATE_SHAPE = _pvc_routes.get(
    "pvc_watch_update_shape_metadata", "updateWatchShape"
)
PVC_WATCH_VALIDATE = _pvc_routes.get("pvc_watch_validate_metdata", "validateWatchPath")
PVC_CHANGE_MAX_ZOOM = _pvc_routes.get("pvc_change_max_zoom", "changeMaxZoom")
PVC_CHANGE_WATCH_MAX_ZOOM = _pvc_routes.get(
    "pvc_change_watch_max_zoom", "changeWatchMaxZoom"
)
PVC_ROOT_DIR = _pvc_routes.get("pvc_root_directory", "/layerSources/watch")

"""
#  s3  #
"""

_s3_credentials = conf.get("s3_credential")
S3_ENDPOINT_URL = _s3_credentials.get("s3_endpoint_url", "https://")
S3_ACCESS_KEY = _s3_credentials.get("s3_access_key", None)
S3_SECRET_KEY = _s3_credentials.get("s3_secret_key", None)
S3_BUCKET_NAME = _s3_credentials.get("s3_bucket_name", "UNKNOWN")
S3_END_POINT = _s3_credentials.get("s3_end_point", None)

"""
#  gql & pycsw  #
"""

_endpoints_discrete_ingestion = conf.get("discrete_ingestion_credential")
PYCSW_URL = _api_route.get("pycsw_url", None)
MAX_ZOOM_TO_CHANGE = _endpoints_discrete_ingestion.get("max_zoom_level", 4)
FAILURE_FLAG = _endpoints_discrete_ingestion.get("failure_tag", False)
PVC_UPDATE_ZOOM = _endpoints_discrete_ingestion.get("change_max_zoom_level", True)
PVC_HANDLER_ROUTE = _endpoints_discrete_ingestion.get("pvc_handler_url", None)
# DISCRETE_JOB_MANAGER_URL = _endpoints_discrete_ingestion.get('agent_url', 'https://')
# PVC_HANDLER_URL = _endpoints_discrete_ingestion.get('pvc_handler_url', 'https://')
# DISCRETE_RAW_ROOT_DIR = _endpoints_discrete_ingestion.get('discrete_raw_root_dir', '/tmp')
# DISCRETE_RAW_SRC_DIR = _endpoints_discrete_ingestion.get('discrete_raw_src_dir', 'ingestion/1')
# DISCRETE_RAW_DST_DIR = _endpoints_discrete_ingestion.get('discrete_raw_dst_dir', 'ingestion/2')
# NFS_RAW_ROOT_DIR = _endpoints_discrete_ingestion.get('nfs_raw_root_dir', '/tmp')
# NFS_RAW_SRC_DIR = _endpoints_discrete_ingestion.get('nfs_raw_src_dir', 'ingestion/1')
# NFS_RAW_DST_DIR = _endpoints_discrete_ingestion.get('nfs_raw_dst_dir', 'ingestion/2')
# INGESTION_TIMEOUT = _endpoints_discrete_ingestion.get('ingestion_timeout', 300)
# BUFFER_TIMEOUT = _endpoints_discrete_ingestion.get('buffer_timeout', 70)

"""
#  pycsw record params  #
"""

_pycsw_records_params = conf.get("pycsw_records_params")
PYCSW_SERVICE = _pycsw_records_params.get("pycsw_service", "CSW")
PYCSW_VERSION = _pycsw_records_params.get("pycsw_version", "2.0.2")
PYCSW_REQUEST_GET_RECORDS = _pycsw_records_params.get(
    "pycsw_request_get_records", "GetRecords"
)
PYCSW_TYPE_NAMES = _pycsw_records_params.get("pycsw_type_names", "mc:MCRasterRecord")
PYCSW_ElEMENT_SET_NAME = _pycsw_records_params.get("pycsw_element_set_name", "full")
PYCSW_OUTPUT_FORMAT = _pycsw_records_params.get(
    "pycsw_output_format", "application/xml"
)
PYCSW_RESULT_TYPE = _pycsw_records_params.get("pycsw_result_type", "results")
PYCSW_OUTPUT_SCHEMA = _pycsw_records_params.get("pycsw_output_schema", None)
PYCSW_REQUEST_GET_CAPABILITIES = _pycsw_records_params.get(
    "pycsw_request_get_capabilities", "GetCapabilities"
)

"""
#  Mock Data params  #
"""

_mock_data = conf.get("mock_data")
MOCK_IMAGERY_RAW_DATA_PATH = _mock_data.get("mock_imagery_data_path")
MOCK_IMAGERY_RAW_DATA_FILE = _mock_data.get("mock_data_file")

"""
# Geopackage params
"""
_geopack_vars = conf.get('overseer_params')
GEO_PACKAGE_SRC_NFS = _geopack_vars.get('geopackage_src_dir_nfs')
GEO_PACKAGE_DEST_NFS = _geopack_vars.get('geopackage_dest_dir_nfs')
GEO_PACKAGE_SRC_PVC = _geopack_vars.get('geopackage_src_dir_pvc')
GEO_PACKAGE_DEST_PVC = _geopack_vars.get('geopackage_dest_dir_pvc')

"""
#  Zoom level limit params  #
"""

_zoom_level_limit_config = conf.get("zoom_level_limit_config")
FIRST_ZOOM_LEVEL = _zoom_level_limit_config.get("first_zoom_level", 4)
SECOND_ZOOM_LEVEL = _zoom_level_limit_config.get("second_zoom_level", 10)
THIRD_ZOOM_LEVEL = _zoom_level_limit_config.get("third_zoom_level", 16)
DIFFERENT_ZOOM_LEVEL_DELAY = _zoom_level_limit_config.get("diff_zoom_level", 60)
DIFFERENT_ZOOM_LEVEL_DELAY_4 = _zoom_level_limit_config.get("diff_zoom_level_4", 90)
DIFFERENT_ZOOM_LEVEL_DELAY_10 = _zoom_level_limit_config.get("diff_zoom_level_10", 180)
DIFFERENT_ZOOM_LEVEL_DELAY_16 = _zoom_level_limit_config.get("diff_zoom_level_16", 360)

PYCSW_GET_RECORD_PARAMS = {
    "service": PYCSW_SERVICE,
    "version": PYCSW_VERSION,
    "request": PYCSW_REQUEST_GET_RECORDS,
    "typenames": PYCSW_TYPE_NAMES,
    "ElementSetName": PYCSW_ElEMENT_SET_NAME,
    # 'outputFormat': PYCSW_OUTPUT_FORMAT,
    "resultType": PYCSW_RESULT_TYPE,
    "outputSchema": PYCSW_OUTPUT_SCHEMA,
}

PYCSW_GET_CAPABILITIES_PARAMS = {
    "service": PYCSW_SERVICE,
    "version": PYCSW_VERSION,
    "request": PYCSW_REQUEST_GET_CAPABILITIES,
}

GQK_URL = _api_route.get("graphql", None)

PYCSW_QUERY_BY_PRODUCTID = {
    "query": """
        query searchme ($opts: SearchOptions, $end: Float, $start: Float){
              search(opts: $opts, end: $end, start: $start) {
                        ... on LayerRasterRecord {
                          __typename
                          productId
                          productName
                          productType
                          sensorType
                          description
                          scale
                          footprint
                          layerPolygonParts
                          type
                          id
                          accuracyCE90
                          sourceDateEnd
                          links {
                            name
                            description
                            protocol
                            url
                          }
                        }
              }
            }
        """,
    "variables": {
        "opts": {
            "filter": [
                {"field": "mc:type", "eq": "RECORD_RASTER"},
                {"field": "mc:productId", "eq": "RECORD_ALL"},
            ]
        },
        # "start": 1,
        # "end": 50
    },
}

# mapping of zoom level and related resolution values
zoom_level_dict = {
    0: 0.703125,
    1: 0.3515625,
    2: 0.17578125,
    3: 0.087890625,
    4: 0.0439453125,
    5: 0.02197265625,
    6: 0.010986328125,
    7: 0.0054931640625,
    8: 0.00274658203125,
    9: 0.001373291015625,
    10: 0.0006866455078125,
    11: 0.00034332275390625,
    12: 0.000171661376953125,
    13: 0.0000858306884765625,
    14: 0.0000429153442382812,
    15: 0.0000214576721191406,
    16: 0.0000107288360595703,
    17: 0.00000536441802978516,
    18: 0.00000268220901489258,
    19: 0.00000134110450744629,
    20: 0.000000670552253723145,
    21: 0.000000335276126861572,
    22: 0.000000167638063430786,
}
