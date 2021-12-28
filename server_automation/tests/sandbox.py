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
s3_c = s3_conn.get_client()

ZOOM_LEVEL_0_TO_4 = list(range(0, 5))
ZOOM_LEVEL_0_TO_10 = list(range(0, 11))
ZOOM_LEVEL_0_TO_16 = list(range(0, 15))
verification_list_0_to_4 = []
verification_list_0_to_10 = []
verification_list_0_to_16 = []
result = s3_c.list_objects(Bucket=config.S3_BUCKET_NAME,
                           Prefix='2021_12_27T13_07_46Z_MAS_6_ORT_247557/4.0/OrthophotoHistory/', Delimiter='/')
for o in result.get('CommonPrefixes'):
    verification_list_0_to_4.append(int(o.get('Prefix').split('/')[-2]))
verification_list_0_to_4.sort()
assert verification_list_0_to_4 == ZOOM_LEVEL_0_TO_16
# print('list_of_tiles')
