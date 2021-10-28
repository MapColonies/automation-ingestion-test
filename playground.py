import json
import jsonschema
from jsonschema import validate
from server_automation.functions.executors import *
from discrete_kit.configuration.config import validate_ext_files_exists

#
from server_automation.ingestion_api.discrete_directory_loader import get_folder_path_by_name


def validate_json_keys(path_to_schema_key, json_to_validate):
    # ToDo : Add path
    missing_keys = []
    pycsw_json_schema = get_json_schema(path_to_schema_key)
    if pycsw_json_schema or json_to_validate is None:
        return False
    else:
        for key in json_to_validate['data']['search'][0].keys():
            if key not in pycsw_json_schema['properties']['data']['properties']['search']['items']['properties'].keys():
                missing_keys.append(key)
                # return False
    return missing_keys


def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value)
        else:
            yield (key, value)


# return True

#
#
# def validate_json(json_data):
#     """REF: https://json-schema.org/ """
#     # Describe what kind of json you expect.
#     execute_api_schema = get_schema()
#     try:
#         validate(instance=json_data, schema=execute_api_schema)
#     except jsonschema.exceptions.ValidationError as err:
#         # err = "Given JSON data is InValid"
#         return False, err
#
#     message = "Given JSON data is Valid"
#     return True, message


# jsonData = json.dumps(myjson)

# validate it
# print(validate_json_keys('user_schema.json', myjson))
# is_valid, msg = validate_json(jsonData)


# print(msg)
#
# for k, v in recursive_items(get_json_schema('pycsw.json')):
#     print(v)
#
#
#
# my_read_json = get_json_schema('pycsw.json')
# print(validate_json_keys('server_automation/configuration/pycsw_validation_schema.json', get_json_schema('pycsw.json')))
# print('d')


shape_json = {'fileNames': ['/X185_Y167.tiff'],
              'metadata': {'type': 'RECORD_RASTER', 'productName': 'O_ayosh_w84geo_Tiff_10cm', 'region': 'ישראל, ירדן',
                           'producerName': 'undefined', 'classification': '9999999999999',
                           'description': 'תשתית אורתופוטו באיזור איו"ש עדכני למאי 2020',
                           'creationDate': '2020-21-05T00:00:00.000Z', 'ingestionDate': '2020-21-05T00:00:00.000Z',
                           'updateDate': '2020-21-05T00:00:00.000Z', 'sourceDateStart': '2020-21-05T00:00:00.000Z',
                           'sourceDateEnd': '2020-21-05T00:00:00.000Z', 'accuracyCE90': 3, 'sensorType': ['UNDEFINED'],
                           'rms': 'undefined', 'scale': 'undefined',
                           'productId': '2021_10_26T15_33_14Z_MAS_6_ORT_247557', 'productVersion': '4.0',
                           'productType': 'Orthophoto', 'resolution': '0.0000185185', 'maxResolutionMeter': 2.0,
                           'footprint': {'type': 'Polygon', 'coordinates': [
                               [[35.172258148995, 31.7732841960024], [35.0884731109971, 31.7732841960024],
                                [35.0884731109971, 31.828506152999], [35.172258148995, 31.828506152999],
                                [35.172258148995, 31.7732841960024]]]}, 'srsName': 'undefined', 'srsId': 'undefined',
                           'layerPolygonParts': {'type': 'FeatureCollection', 'features': [{'type': 'Feature',
                                                                                            'properties': {
                                                                                                'Cities': "ג'נין, ירושלים, יריחו, שכם",
                                                                                                'Countries': 'ישראל, ירדן',
                                                                                                'Dsc': 'תשתית אורתופוטו באיזור איו"ש עדכני למאי 2020',
                                                                                                'Ep90': '3',
                                                                                                'Resolution': '0.1',
                                                                                                'Rms': None,
                                                                                                'Scale': None,
                                                                                                'SensorType': 'OTHER',
                                                                                                'Source': '2021_10_26T15_33_14Z_MAS_6_ORT_247557-4.0',
                                                                                                'SourceName': 'O_ayosh_w84geo_Tiff_10cm',
                                                                                                'UpdateDate': '21/05/2020'},
                                                                                            'geometry': {
                                                                                                'type': 'Polygon',
                                                                                                'coordinates': [[[
                                                                                                    35.1722581489948,
                                                                                                    31.7732841960031],
                                                                                                    [
                                                                                                        35.0884731110009,
                                                                                                        31.7732841960031],
                                                                                                    [
                                                                                                        35.0884731110009,
                                                                                                        31.8285061529974],
                                                                                                    [
                                                                                                        35.1722581489948,
                                                                                                        31.8285061529974],
                                                                                                    [
                                                                                                        35.1722581489948,
                                                                                                        31.7732841960031]]]}}],
                                                 'bbox': [35.0884731109971, 31.7732841960024, 35.172258148995,
                                                          31.828506152999]}, 'includedInBests': 'undefined',
                           'productBoundingBox': 'undefined'}, 'originDirectory': 'test_data_automation/Shapes'}
pycsw_json = {
    "data": {
        "search": [
            {
                "__typename": "LayerRasterRecord",
                "productId": "2021_10_26T08_53_17Z_MAS_6_ORT_247993",
                "productName": "O_arzi_mz_20cm",
                "productType": "ORTHOPHOTO",
                "sensorType": [
                    "UNDEFINED"
                ],
                "description": "\u05ea\u05e9\u05ea\u05d9\u05ea \u05d0\u05d5\u05e8\u05ea\u05d5\u05e4\u05d5\u05d8\u05d5 \u05d1\u05d9\u05e9\u05e8\u05d0\u05dc \u05e2\u05d3\u05db\u05e0\u05d9 \u05dc\u05d0\u05e4\u05e8\u05d9\u05dc 2019",
                "scale": None,
                "footprint": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                34.8468438649828,
                                32.0689996810298
                            ],
                            [
                                34.8637856279928,
                                32.0590059440186
                            ],
                            [
                                34.8773961450173,
                                32.0680478960404
                            ],
                            [
                                34.8804418550117,
                                32.0528193460686
                            ],
                            [
                                34.8786334639958,
                                32.0466327470143
                            ],
                            [
                                34.8605495609931,
                                32.0488218510146
                            ],
                            [
                                34.8468438649828,
                                32.0689996810298
                            ]
                        ]
                    ]
                },
                "layerPolygonParts": {
                    "bbox": [
                        34.8468438649828,
                        32.0466327470143,
                        34.8804418550117,
                        32.0689996810298
                    ],
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [
                                            34.8468438649828,
                                            32.0689996810298
                                        ],
                                        [
                                            34.8637856279928,
                                            32.0590059440186
                                        ],
                                        [
                                            34.8773961450173,
                                            32.0680478960404
                                        ],
                                        [
                                            34.8804418550117,
                                            32.0528193460686
                                        ],
                                        [
                                            34.8786334639958,
                                            32.0466327470143
                                        ],
                                        [
                                            34.8605495609931,
                                            32.0488218510146
                                        ],
                                        [
                                            34.8468438649828,
                                            32.0689996810298
                                        ]
                                    ]
                                ]
                            },
                            "properties": {
                                "Dsc": "\u05ea\u05e9\u05ea\u05d9\u05ea \u05d0\u05d5\u05e8\u05ea\u05d5\u05e4\u05d5\u05d8\u05d5 \u05d1\u05d9\u05e9\u05e8\u05d0\u05dc \u05e2\u05d3\u05db\u05e0\u05d9 \u05dc\u05d0\u05e4\u05e8\u05d9\u05dc 2019",
                                "Rms": None,
                                "Ep90": "3",
                                "Scale": None,
                                "Source": "2021_10_26T08_53_17Z_MAS_6_ORT_247993-1.0",
                                "Resolution": "0.2",
                                "SensorType": "OTHER",
                                "SourceName": "O_arzi_mz_w84geo_Tiff_20cm",
                                "UpdateDate": "06/04/2019"
                            }
                        }
                    ]
                },
                "type": "RECORD_RASTER",
                "id": "95b886c9-8ff6-4084-ab55-a0c574903819",
                "accuracyCE90": 3,
                "sourceDateEnd": None,
                "links": [
                    {
                        "name": None,
                        "description": None,
                        "protocol": "WMS",
                        "url": "http://mapproxy-qa-map-proxy-map-proxy-route-raster.apps.v0h0bdx6.eastus.aroapp.io/service?REQUEST=GetCapabilities"
                    },
                    {
                        "name": None,
                        "description": None,
                        "protocol": "WMTS",
                        "url": "http://mapproxy-qa-map-proxy-map-proxy-route-raster.apps.v0h0bdx6.eastus.aroapp.io/wmts/1.0.0/WMTSCapabilities.xml"
                    },
                    {
                        "name": None,
                        "description": None,
                        "protocol": "WMTS_LAYER",
                        "url": "http://mapproxy-qa-map-proxy-map-proxy-route-raster.apps.v0h0bdx6.eastus.aroapp.io/wmts/2021_10_26T08_53_17Z_MAS_6_ORT_247993-Orthophoto/{TileMatrixSet}/{TileMatrix}/{TileCol}/{TileRow}.png"
                    }
                ]
            }
        ]
    }
}

from discrete_kit.validator.json_compare_pycsw import *

# state, err = validate_pycsw_with_shape_json(pycsw_json, shape_json)
# print(err)
#
# print(state)
def kuku(tiff_name):
    ap = []
    for item in tiff_name:
        ap.append(validate_ext_files_exists(os.path.join('/tmp/ingestion/watch/test_data_automation/7b812f28-0141-4257-a5b1-22cb94dc1793/O_ayosh_w84geo_Apr17-May20_tiff_2/MAS_6_ORT_247557_29793-1.0/Pyramid0_1','X185_Y167'),'.tif'))
    return ap

myjs = {'fileNames': ['/X185_Y167.tiff'], 'metadata': {'type': 'RECORD_RASTER', 'productName': 'O_ayosh_w84geo_Tiff_10cm', 'region': 'ישראל, ירדן', 'producerName': 'undefined', 'classification': '9999999999999', 'description': 'תשתית אורתופוטו באיזור איו"ש עדכני למאי 2020', 'creationDate': '2020-21-05T00:00:00.000Z', 'ingestionDate': '2020-21-05T00:00:00.000Z', 'updateDate': '2020-21-05T00:00:00.000Z', 'sourceDateStart': '2020-21-05T00:00:00.000Z', 'sourceDateEnd': '2020-21-05T00:00:00.000Z', 'accuracyCE90': 3, 'sensorType': ['UNDEFINED'], 'rms': 'undefined', 'scale': 'undefined', 'productId': '2021_10_27T13_46_37Z_MAS_6_ORT_247557', 'productVersion': '4.0', 'productType': 'Orthophoto', 'resolution': '0.0000185185', 'maxResolutionMeter': 2.0, 'footprint': {'type': 'Polygon', 'coordinates': [[[35.172258148995, 31.7732841960024], [35.0884731109971, 31.7732841960024], [35.0884731109971, 31.828506152999], [35.172258148995, 31.828506152999], [35.172258148995, 31.7732841960024]]]}, 'srsName': 'undefined', 'srsId': 'undefined', 'layerPolygonParts': {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'Cities': "ג'נין, ירושלים, יריחו, שכם", 'Countries': 'ישראל, ירדן', 'Dsc': 'תשתית אורתופוטו באיזור איו"ש עדכני למאי 2020', 'Ep90': '3', 'Resolution': '0.1', 'Rms': None, 'Scale': None, 'SensorType': 'OTHER', 'Source': '2021_10_27T13_46_37Z_MAS_6_ORT_247557-4.0', 'SourceName': 'O_ayosh_w84geo_Tiff_10cm', 'UpdateDate': '21/05/2020'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[35.1722581489948, 31.7732841960031], [35.0884731110009, 31.7732841960031], [35.0884731110009, 31.8285061529974], [35.1722581489948, 31.8285061529974], [35.1722581489948, 31.7732841960031]]]}}], 'bbox': [35.0884731109971, 31.7732841960024, 35.172258148995, 31.828506152999]}, 'includedInBests': 'undefined', 'productBoundingBox': 'undefined'}, 'originDirectory': '7b812f28-0141-4257-a5b1-22cb94dc1793/Shapes'}

print(kuku(myjs['fileNames']))

