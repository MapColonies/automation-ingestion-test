[![Python 3.6](https://img.shields.io/badge/python-3.6-green.svg)](https://www.python.org/downloads/release/python-360/)
<img alt="GitHub release (latest by date including pre-releases)" src="https://img.shields.io/github/v/release/MapColonies/automation-ingestion-test">

# Automation-ingestion-test
This repo provide full set of test responsible of Discrete Ingestion services based on MC project requirements

## Test suite include following tests:
1. Ingestion of new discrete layer into system:
    1. Manuel ingestion
    2. Auto ingestion by agent watch
2. Ingestion discrete partial update - NOT IMPLEMENTED
3. Best Management - NOT IMPLEMENTED


## Run & Deployment:
1. This repo can run tests as:
    1. Local package
    2. Docker
    
2. 


#### Runtime Environment variables        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| TEST_ENV | environment running on - running on default with PVC mode| - | QA | 
| DEBUG_MODE_LOCAL | extended internal flows on flag - BOOL| - | False | 
| SYSTEM_DELAY   | Mutual delay value - seconds | - | 5 | 
| FOLLOW_TIMEOUT   | Value for internal timeout for follow ingestion function - minutes | - | 10 | 
| INGESTION_AGENT_URL | Route url for ingestion rest API services | + | from environment specification | 
| CLEAN_UP | Flag for environment cleanup on test ending - BOOL | - | False | 


##### S3 Environment variables [ optional environment variables ]        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| S3_END_POINT | Endpoint url of S3 server | + | from environment specification | 
| S3_BUCKET_NAME | Bucket name | + | raster | 
| S3_SECRET_KEY | Secret key | + | from environment specification |
| S3_ACCESS_KEY | Access key | + | from environment specification |


#####Postgress Environment variables [ optional variables for debug running ]        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| PG_HOST | Endpoint url of server | + | from environment specification | 
| PG_USER | User name credential | + | from environment specification | 
| PG_PASS | Password credential | + | from environment specification |
| PG_JOB_TASK_DB_NAME | Job & Task table name | + | from environment specification |
| PG_RECORD_PYCSW_DB | Discrete pycsw record table name | + | from environment specification |
| PG_AGENT | Agent manager table name | + | from environment specification |
| PG_MAPPROXY_CONFIG   | mapproxy upload configuration table | + | from environment specification |


##### NFS Environment variables [ optional environment variables - when running with NFS ]        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| NFS_ROOT_DIR | Base directory | - | /tmp | 
| NFS_SOURCE_DIR | Relative path of source data | - | ingestion/1 | 
| NFS_DEST_DIR | Relative destination test path of copied data | - | ingestion/2 |


#####Persistent volume claim Handler - Environment variables [ optional variables for environment without NFS ]        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| PVC_ROOT_DIR | Base configurable folder | + | layerSources |
| PVC_HANDLER_ROUTE | Endpoint url of server | + | from environment specification | 
| PVC_CLONE_SOURCE | Manuel ingest source data duplicate - route | + | createTestDir | 
| PVC_CHANGE_METADATA | Manuel ingest source id update - route | + | updateShape | 
| PVC_VALIDATE_METADATA | Manuel ingest source data validator - route | + | validatePath |
| PVC_WATCH_CREATE_DIR | Watch ingest source data duplicate - route | + | createWatchDir |
| PVC_WATCH_UPDATE_SHAPE | Watch ingest source id update - route | + | updateWatchShape |
| PVC_WATCH_VALIDATE   | Watch ingest source data validator - route | + | validateWatchPath |