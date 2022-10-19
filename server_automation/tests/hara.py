from mc_automation_tools import s3storage

from server_automation.configuration import config


product_name = "2022_08_24T06_09_03Z_MAS_6_ORT_247557"

s3_conn = s3storage.S3Client(
    config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY
)

list_of_tiles = s3_conn.list_folder_content(
    "raster-qa", "2022_08_24T06_09_03Z_MAS_6_ORT_247557"
)
