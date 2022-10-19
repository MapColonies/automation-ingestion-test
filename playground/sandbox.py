# # # cleanup_states = {}
# # # # cleanup_states = {"job_folder_cleanup": job_folder_cleanup()}
# # # cleanup_states = {"db_cleanup": db_cleanup('2021_12_09T11_44_22Z_MAS_6_ORT_247557','4.0')}
# # # # cleanup_states = {"tiles_cleanup": tiles_cleanup()}
# # # # cleanup_states = {"db_cleanup": tiles_cleanup()}
# # # # cleanup_states = {"restore_watch_state": restore_watch_state()}
# # #
# # #
# # # from mc_automation_tools import s3storage as s3
# # # from server_automation.configuration import config
# # #
# # # s3_conn = s3.S3Client(config.S3_END_POINT, config.S3_ACCESS_KEY, config.S3_SECRET_KEY)
# # # s3_c = s3_conn.get_client()
# # #
# # # ZOOM_LEVEL_0_TO_4 = list(range(0, 5))
# # # ZOOM_LEVEL_0_TO_10 = list(range(0, 11))
# # # ZOOM_LEVEL_0_TO_16 = list(range(0, 15))
# # # verification_list_0_to_4 = []
# # # verification_list_0_to_10 = []
# # # verification_list_0_to_16 = []
# # # result = s3_c.list_objects(
# # #     Bucket=config.S3_BUCKET_NAME,
# # #     Prefix="2021_12_27T13_07_46Z_MAS_6_ORT_247557/4.0/OrthophotoHistory/",
# # #     Delimiter="/",
# # # )
# # # for o in result.get("CommonPrefixes"):
# # #     verification_list_0_to_4.append(int(o.get("Prefix").split("/")[-2]))
# # # verification_list_0_to_4.sort()
# # # assert verification_list_0_to_4 == ZOOM_LEVEL_0_TO_16
# # # # print('list_of_tiles')
# #
# # def is_valid_zoom_for_area(resolution, bbox):
# #     """
# #     Return true if bbox is at least 1 pixle at the wanted resolution, false otherwise.
# #     """
# #     top_right_lat = bbox[3]
# #     top_right_lon = bbox[2]
# #     bottom_left_lat = bbox[1]
# #     bottom_left_lon = bbox[0]
# #
# #     # Check if bbox width and height are at least at the resolution of a pixle at the wanted zoom level
# #     return (top_right_lon - bottom_left_lon) > float(resolution) and (top_right_lat - bottom_left_lat) > float(resolution)
# #
# #
# #
# # # print(is_valid_zoom_for_area(0.0439453125,[35.0884731110009,31.7732841960031,35.1722581489948,31.8285061529974]))
# # dod = [[[34.2765670343669, 31.1786172883581], [34.2663935002085, 31.2050281994541], [34.2666867110507, 31.2055612191636], [34.2672744001369, 31.2065806002331], [34.268973399954, 31.2066233999487], [34.2689772001245, 31.2070429001308], [34.2718911998544, 31.2078455999738], [34.2736871990614, 31.208393799754], [34.2885093000768, 31.212380800015], [34.2884903000914, 31.2128566996497], [34.2875194997442, 31.215502700596], [34.2850252000538, 31.2215894999033], [34.2861245014355, 31.2220036004238], [34.295418699988, 31.2248017999879], [34.2990048000058, 31.2161012999914], [34.3106759999975, 31.219491999989], [34.3070354999829, 31.2286292000186], [34.3177429999876, 31.23180570002], [34.3210266999625, 31.2232397000376], [34.3258773627451, 31.2246867020347], [34.3255089159995, 31.179183557997], [34.2765670343669, 31.1786172883581]]]
# #
# #
# # print(len(dod))
# #
# #
# # # print(type(dod))
# import asyncio
# import time
# from textwrap import dedent
#
# import pytest
#
# # print(dedent("""
# # The Gothons of Planet Percal #25 have invaded your ship and
# # 6 destroyed your entire crew. You are the last surviving
# # 7 member and your last mission is to get the neutron destruct
# # 8 bomb from the Weapons Armory, put it in the bridge, and
# # 9 blow the ship up after getting into an escape pod.
# # 10
# # 11 You're running down the central corridor to the Weapons
# # 12 Armory when a Gothon jumps out, red scaly skin, dark grimy
# # 13 teeth, and evil clown costume flowing around his hate
# # 14 filled body. He's blocking the door to the Armory and
# # 15 about to pull a weapon to blast you.
# # """))
#
#
# @pytest.fixture
# def input_value():
#     input = 39
#     return input
#
#
# def test_divisible_by_3(input_value):
#     assert input_value % 3 == 0
#
#
# def test_divisible_by_6(input_value):
#     assert input_value % 6 == 3
