# automation-ingestion-test
This repo provide full set of test responsible of Discrete Ingestion services based on MC project requirements

-e TEST_ENV=QA \
-e NFS_ROOT_DIR=/tmp \
-e NFS_SOURCE_DIR=ingestion/1 \
-e NFS_DEST_DIR=ingestion/2 \
-e INGESTION_AGENT_URL=https://discrete-agent-qa-agent-route-raster.apps.v0h0bdx6.eastus.aroapp.io \
-e S3_ACCESS_KEY=raster \
-e S3_SECRET_KEY=rasterPassword \
-e S3_BUCKET_NAME=raster \
-e DEBUG_MODE_LOCAL=false \
-e CLEAN_UP=True \
-e SYSTEM_DELAY=50 \
-e FOLLOW_TIMEOUT=1 \

###Runtime Environment variables        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| ENVIRONMENT_NAME | environment running on | + | dev | 
| EXPORTER_TRIGGER_API | full uri of trigger api | + | from environment specification | 
| MAX_EXPORT_RUNNING_TIME   | integer represent min for run timeout | - | 5 | 
| RUNNING_WORKERS_NUMBER   | depends on system configuration | - | 1 | 
| TMP_DIR | internal temp directory | in case of File system mode | /tmp/auto-exporter | 
| DEBUG_LOGS | any value for debug logs | - | None | 
| FILE_LOGS | any value for logs file output | - | None | 
| LOGS_OUTPUT | permitted directory for logs file output | in case of FILE_LOGS=1 | /tmp/mc_logs |
| BEST_LAYER_URL   | relevant layer url | + | provided on exported chart | 
| SOURCE_LAYER | source layer name | + | provided on exported chart |
| S3_EXPORT_STORAGE_MODE   | true for object storage mode | in case of prod environment(openshift) | False | 
| S3_DOWNLOAD_DIR | valid directory downloading data from S3 | in case of S3 mode | /tmp | 
| S3_BUCKET_NAME | export output bucket name | in case of S3 mode | provided from secret | 
| S3_ACCESS_KEY | AWS access key | in case of S3 mode | provided from secret |
| S3_SECRET_KEY | AWS secret key | in case of S3 mode | provided from secret | 
| S3_END_POINT | Storage procided endpoint | in case of S3 mode | provided from secret | 
| USE_JIRA | true for updating jira's specific cycle | - | False | 
| JIRA_CONF | Directory of configuration json | - | placed locally | \

####S3 Environment variables [ optional environment variables ]        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| S3_END_POINT | Endpoint url of server | + | from environment specification | 
| S3_BUCKET_NAME | User name credential | + | raster | 
| PG_PASS | Password credential | + | from environment specification |
| PG_JOB_TASK_DB_NAME | Job & Task table name | + | from environment specification |
| PG_RECORD_PYCSW_DB | Discrete pycsw record table name | + | from environment specification |
| PG_AGENT | Agent manager table name | + | from environment specification |
| PG_MAPPROXY_CONFIG   | mapproxy upload configuration table | + | from environment specification |


####Postgress Environment variables [ optional variables for debug running ]        
|  Variable   | Value       | Mandatory   |   Default   |
| :----------- | :-----------: | :-----------: | :-----------: |
| PG_HOST | Endpoint url of server | + | from environment specification | 
| PG_USER | User name credential | + | from environment specification | 
| PG_PASS | Password credential | + | from environment specification |
| PG_JOB_TASK_DB_NAME | Job & Task table name | + | from environment specification |
| PG_RECORD_PYCSW_DB | Discrete pycsw record table name | + | from environment specification |
| PG_AGENT | Agent manager table name | + | from environment specification |
| PG_MAPPROXY_CONFIG   | mapproxy upload configuration table | + | from environment specification |


####Persistent volume claim Handler - Environment variables [ optional variables for environment without NFS ]        
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