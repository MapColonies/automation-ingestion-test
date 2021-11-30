""" configuration for running ingestion tests"""
from mc_automation_tools import common
import enum


class EnvironmentTypes(enum.Enum):
    """
    Types of environment.
    """
    QA = 1
    DEV = 2
    PROD = 3


class ResponseCode(enum.Enum):
    """
    Types of server responses
    """
    Ok = 200  # server return ok status
    ChangeOk = 201  # server was return ok for changing
    ValidationErrors = 400  # bad request
    StatusNotFound = 404  # status\es not found on db
    DuplicatedError = 409  # in case of requesting package with same name already exists
    GetwayTimeOut = 504  # some server didn't respond
    ServerError = 500  # problem with error


class JobStatus(enum.Enum):
    """
    Types of job statuses
    """
    Completed = 'Completed'
    Failed = 'Failed'
    InProgress = 'In-Progress'
    Pending = 'Pending'


############################################  general running environment  #############################################
CLEAN_UP = common.get_environment_variable('CLEAN_UP', False)  # If should clean running data from env at the end
DEBUG_MODE_LOCAL = common.get_environment_variable('DEBUG_MODE_LOCAL', False)  # for multiple debug option on dev
FOLLOW_TIMEOUT = 60 * common.get_environment_variable('FOLLOW_TIMEOUT', 10)
SYSTEM_DELAY = common.get_environment_variable('SYSTEM_DELAY', 60)
TEST_ENV = common.get_environment_variable('TEST_ENV', EnvironmentTypes.QA.name)  # compatibility to azure + prod env
VALIDATION_SWITCH = common.get_environment_variable('VALIDATION_SWITCH',
                                                    True)  # if false -> will skip data validation scopes

FAILURE_FLAG = common.get_environment_variable('FAILURE_FLAG', False)
ORIG_DISCRETE_PATH = common.get_environment_variable('ORIG_DISCRETE_PATH',
                                                     '/home/ronenk1/dev/automation-server-test/shp/1')
SHAPES_PATH = common.get_environment_variable('SHAPES_PATH', 'Shapes')
TIFF_PATH = common.get_environment_variable('TIFF_PATH', 'tiff')
# SHAPE_FILE_LIST = ['Files.dbf', 'Product.shp', 'Product.dbf', 'ShapeMetadata.shp', 'ShapeMetadata.dbf']
SHAPE_FILE_LIST = ['Files.shp', 'Files.dbf', 'Product.shp', 'Product.dbf', 'ShapeMetadata.shp', 'ShapeMetadata.dbf']
SHAPE_METADATA_FILE = common.get_environment_variable('SHAPE_METADATA_FILE', 'ShapeMetadata.shp')
##########################################  Ingestion API's sub urls & API's  ##########################################
INGESTION_MANUAL_TRIGGER = 'trigger'
INGESTION_WATCHER_STATUS = 'status'
INGESTION_START_WATCHER = 'start'
INGESTION_STOP_WATCHER = 'stop'
INGESTION_AGENT_URL = common.get_environment_variable('INGESTION_AGENT_URL',
                                                      'https://discrete-agent-dev-agent-route-raster-dev.apps.v0h0bdx6.eastus.aroapp.io')
################################################  MAPPROXY VARIABELS  ##################################################
WMS = 'WMS'
WMTS = 'WMTS'
WMTS_LAYER = 'WMTS_LAYER'
###############################################  POSTGRESS CREDENTIALS  ################################################
PG_USER = common.get_environment_variable('PG_USER', None)
PG_PASS = common.get_environment_variable('PG_PASS', None)
PG_HOST = common.get_environment_variable('PG_HOST', None)
PG_JOB_TASK_DB_NAME = common.get_environment_variable('PG_JOB_TASK_DB_NAME', None)
PG_RECORD_PYCSW_DB = common.get_environment_variable('PG_RECORD_PYCSW_DB', None)
PG_MAPPROXY_CONFIG = common.get_environment_variable('PG_MAPPROXY_CONFIG', None)
PG_PYCSW_RECORD = common.get_environment_variable('PG_PYCSW_RECORD', None)
PG_AGENT = common.get_environment_variable('PG_AGENT', None)

####################################################  environment  #####################################################
PVC_HANDLER_ROUTE = common.get_environment_variable('PVC_HANDLER_ROUTE', None)
PVC_CLONE_SOURCE = common.get_environment_variable('PVC_CLONE_SOURCE', None)
PVC_CHANGE_METADATA = common.get_environment_variable('PVC_CHANGE_METADATA', None)
PVC_VALIDATE_METADATA = common.get_environment_variable('PVC_VALIDATE_METADATA', None)
PVC_ROOT_DIR = common.get_environment_variable('PVC_ROOT_DIR', None)

NFS_ROOT_DIR = common.get_environment_variable('NFS_ROOT_DIR', '/tmp')
NFS_ROOT_DIR_DEST = common.get_environment_variable('NFS_ROOT_DIR_DEST', '/tmp')

NFS_SOURCE_DIR = common.get_environment_variable('NFS_SOURCE_DIR', 'ingestion/1')
NFS_DEST_DIR = common.get_environment_variable('NFS_DEST_DIR', 'test_data')
NFS_TILES_DIR = common.get_environment_variable('NFS_TILES_DIR', '/tmp')

PVC_HANDLER_ROUTE = common.get_environment_variable('PVC_HANDLER_ROUTE', None)
PVC_CLONE_SOURCE = common.get_environment_variable('PVC_CLONE_SOURCE', 'createTestDir')
PVC_CHANGE_METADATA = common.get_environment_variable('PVC_CHANGE_METADATA', 'updateShape')
PVC_CHANGE_WATCH_METADATA = common.get_environment_variable('PVC_CHANGE_WATCH_METADATA', 'updateWatchShape')
PVC_VALIDATE_METADATA = common.get_environment_variable('PVC_VALIDATE_METADATA', 'validatePath')
PVC_ROOT_DIR = common.get_environment_variable('PVC_ROOT_DIR', '/layerSources/watch')
PVC_DELETE_DIR = common.get_environment_variable('PVC_DELETE_DIR', 'deleteTestDir')

PVC_WATCH_CREATE_DIR = common.get_environment_variable('PVC_WATCH_CREATE_DIR', 'createWatchDir')
PVC_WATCH_UPDATE_SHAPE = common.get_environment_variable('PVC_WATCH_UPDATE_SHAPE', 'updateWatchShape')
PVC_WATCH_VALIDATE = common.get_environment_variable('PVC_WATCH_VALIDATE', 'validateWatchPath')

PVC_UPDATE_ZOOM = common.get_environment_variable('PVC_UPDATE_ZOOM', None)  # default not change max zoom
PVC_CHANGE_MAX_ZOOM = common.get_environment_variable('PVC_CHANGE_MAX_ZOOM', 'changeMaxZoom')
PVC_CHANGE_WATCH_MAX_ZOOM = common.get_environment_variable('PVC_CHANGE_WATCH_MAX_ZOOM', 'changeWatchMaxZoom')
MAX_ZOOM_TO_CHANGE = common.get_environment_variable('MAX_ZOOM_TO_CHANGE', 5)

NFS_WATCH_ROOT_DIR = common.get_environment_variable('NFS_WATCH_ROOT_DIR', '/tmp')
NFS_WATCH_SOURCE_DIR = common.get_environment_variable('NFS_WATCH_SOURCE_DIR', 'ingestion/1')
NFS_WATCH_BASE_DIR = common.get_environment_variable('NFS_WATCH_SOURCE_DIR', 'ingestion/1')
NFS_WATCH_DEST_DIR = common.get_environment_variable('NFS_WATCH_DEST_DIR', 'watch')

########################################################  s3  ##########################################################
S3_ACCESS_KEY = common.get_environment_variable('S3_ACCESS_KEY', None)
S3_SECRET_KEY = common.get_environment_variable('S3_SECRET_KEY', None)
S3_BUCKET_NAME = common.get_environment_variable('S3_BUCKET_NAME', None)
S3_END_POINT = common.get_environment_variable('S3_END_POINT', None)

###################################################  gql & pycsw  ######################################################
PYCSW_URL = common.get_environment_variable('PYCSW_URL',
                                            "http://raster-qa-catalog-raster-catalog-pycsw-route-raster.apps.v0h0bdx6.eastus.aroapp.io")
PYCSW_SERVICE = common.get_environment_variable("PYCSW_SERVICE", "CSW")
PYCSW_VERSION = common.get_environment_variable("PYCSW_VERSION", "2.0.2")
PYCSW_REQUEST_GET_RECORDS = common.get_environment_variable("PYCSW_REQUEST_GET_RECORDS", "GetRecords")
PYCSW_TYPE_NAMES = common.get_environment_variable("PYCSW_TYPE_NAMES", "mc:MCRasterRecord")
PYCSW_ElEMENT_SET_NAME = common.get_environment_variable("PYCSW_ElEMENT_SET_NAME", "full")
PYCSW_OUTPUT_FORMAT = common.get_environment_variable("PYCSW_OUTPUT_FORMAT", "application/xml")
PYCSW_RESULT_TYPE = common.get_environment_variable("PYCSW_RESULT_TYPE", "results")
PYCSW_OUTPUT_SCHEMA = common.get_environment_variable("PYCSW_OUTPUT_SCHEMA", "http://schema.mapcolonies.com/raster")

PYCSW_REQUEST_GET_CAPABILITIES = common.get_environment_variable("PYCSW_REQUEST_RECORDS", "GetCapabilities")

PYCSW_GET_RECORD_PARAMS = {
    'service': PYCSW_SERVICE,
    'version': PYCSW_VERSION,
    'request': PYCSW_REQUEST_GET_RECORDS,
    'typenames': PYCSW_TYPE_NAMES,
    'ElementSetName': PYCSW_ElEMENT_SET_NAME,
    # 'outputFormat': PYCSW_OUTPUT_FORMAT,
    'resultType': PYCSW_RESULT_TYPE,
    'outputSchema': PYCSW_OUTPUT_SCHEMA
}

PYCSW_GET_CAPABILITIES_PARAMS = {
    'service': PYCSW_SERVICE,
    'version': PYCSW_VERSION,
    'request': PYCSW_REQUEST_GET_CAPABILITIES
}

GQK_URL = common.get_environment_variable('GQK_URL',
                                          'https://https-bff-raster.apps.v0h0bdx6.eastus.aroapp.io/graphql')
# GQK_URL = common.get_environment_variable('GQK_URL',
#                                           'http://discrete-layer-client-qa-bff-route-raster.apps.v0h0bdx6.eastus.aroapp.io/graphql')


PYCSW_QUERY_BY_PRODUCTID = {
    'query':
        """
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
        """
    ,
    'variables':
        {

            "opts": {
                "filter": [
                    {
                        "field": "mc:type",
                        "eq": "RECORD_RASTER"
                    },
                    {
                        "field": "mc:productId",
                        "eq": "RECORD_ALL"
                    }
                ]
            },
            # "start": 1,
            # "end": 50

        }
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
    22: 0.000000167638063430786
}
