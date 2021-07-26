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
    ChangeOk = 201 # server was return ok for changing
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


ORIG_DISCRETE_PATH = common.get_environment_variable('ORIG_DISCRETE_PATH',
                                                     '/home/ronenk1/dev/automation-server-test/shp/1')
SHAPES_PATH = common.get_environment_variable('SHAPES_PATH', 'Shapes')
TIFF_PATH = common.get_environment_variable('TIFF_PATH', 'tiff')
# SHAPE_FILE_LIST = ['Files.dbf', 'Product.shp', 'Product.dbf', 'ShapeMetadata.shp', 'ShapeMetadata.dbf']
SHAPE_FILE_LIST = ['Files.shp', 'Files.dbf', 'Product.shp', 'Product.dbf', 'ShapeMetadata.shp', 'ShapeMetadata.dbf']

##########################################  Ingestion API's sub urls & API's  ##########################################
INGESTION_MANUAL_TRIGGER = 'trigger'
INGESTION_WATCHER_STATUS = 'status'
INGESTION_START_WATCHER = 'start'
INGESTION_STOP_WATCHER = 'stop'
INGESTION_AGENT_URL = common.get_environment_variable('INGESTION_AGENT_URL',
                                                      'https://discrete-agent-dev-agent-route-raster-dev.apps.v0h0bdx6.eastus.aroapp.io')

###############################################  POSTGRESS CREDENTIALS  ################################################
PG_USER = common.get_environment_variable('PG_USER', None)
PG_PASS = common.get_environment_variable('PG_PASS', None)
PG_HOST = common.get_environment_variable('PG_HOST', None)
PG_JOB_TASK_DB_NAME = common.get_environment_variable('PG_JOB_TASK_DB_NAME', None)

FOLLOW_TIMEOUT = common.get_environment_variable('FOLLOW_TIMEOUT', 5)


####################################################  environment  #####################################################
TEST_ENV = common.get_environment_variable('TEST_ENV', EnvironmentTypes.QA.name)
PVC_HANDLER_ROUTE = common.get_environment_variable('PVC_HANDLER_ROUTE', None)
PVC_CLONE_SOURCE = common.get_environment_variable('PVC_CLONE_SOURCE', None)
PVC_CHANGE_METADATA = common.get_environment_variable('PVC_CHANGE_METADATA', None)

NFS_ROOT_DIR = common.get_environment_variable('NFS_ROOT_DIR', '/tmp')
NFS_SOURCE_DIR = common.get_environment_variable('NFS_SOURCE_DIR', 'ingestion/1')
NFS_DEST_DIR = common.get_environment_variable('NFS_DEST_DIR', 'test_data')
