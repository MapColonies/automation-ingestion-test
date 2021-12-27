# from server_automation.functions.executors import *
#
# cleanup_states = {}
# # cleanup_states = {"job_folder_cleanup": job_folder_cleanup()}
# cleanup_states = {"db_cleanup": db_cleanup('2021_12_09T11_44_22Z_MAS_6_ORT_247557','4.0')}
# # cleanup_states = {"tiles_cleanup": tiles_cleanup()}
# # cleanup_states = {"db_cleanup": tiles_cleanup()}
# # cleanup_states = {"restore_watch_state": restore_watch_state()}
#

from mc_automation_tools import s3storage as s3
from server_automation.configuration import config

s3_conn = s3.S3Client(config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY)
list_of_tiles = s3_conn.list_folder_content(config.S3_BUCKET_NAME,
                                            "/".join(['2021_12_27T13_07_46Z_MAS_6_ORT_247557', '4.0']))
print(list_of_tiles)
