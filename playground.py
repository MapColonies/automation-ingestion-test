# import json
#
# import jsonschema
# from discrete_kit.configuration.config import validate_ext_files_exists
# from jsonschema import validate
#
# from server_automation.functions.executors import *
# from server_automation.ingestion_api.discrete_directory_loader import (
#     get_folder_path_by_name,
# )
#
# #
#
# job_task_handler = job_manager_api.JobsTasksManager(config.JOB_MANAGER_URL)
#
# print(
#     job_task_handler.updates_job(
#         "01140c91-efa7-4f8b-8edd-902f5728a048", {"priority": 15000}
#     )
# )
#
# #
# # def validate_json_keys(path_to_schema_key, json_to_validate):
# #     # ToDo : Playground check if needed.
# #     missing_keys = []
# #     pycsw_json_schema = get_json_schema(path_to_schema_key)
# #     if pycsw_json_schema or json_to_validate is None:
# #         return False
# #     else:
# #         for key in json_to_validate['data']['search'][0].keys():
# #             if key not in pycsw_json_schema['properties']['data']['properties']['search']['items']['properties'].keys():
# #                 missing_keys.append(key)
# #                 # return False
# #     return missing_keys
# #
# #
# # def recursive_items(dictionary):
# #     for key, value in dictionary.items():
# #         if type(value) is dict:
# #             yield from recursive_items(value)
# #         else:
# #             yield (key, value)
# #
