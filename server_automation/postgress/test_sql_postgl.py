# By Shay perpinial not to GIT . LOCAL CHECK.
from server_automation.configuration import config

from server_automation.postgress.sql_helper import SqlHelper
from mc_automation_tools.postgres import PGClass


def sql_main():
    table_data = 'product_name'
    value = '_ayosh_10cm'
    id_pro = "test-update"
    table_col = "product_id"
    table_source = '"RasterCatalogManager".records'
    v = None
    pg = PGClass(host=config.PG_HOST, database=config.PG_JOB_TASK_DB_NAME, user=config.PG_USER,
                 password=config.PG_PASS, scheme=config.SCHEMA_RASTER_CATALOG_MANAGER, port=5432)

    client = pg.get_SqlHelper()
    client.build_query(results_to_get=v, table_name=table_source,
                       search_data=table_data, data=value, operator='end')
    res = client.execute_all()
    print(res)
    test_a = pg.get_SqlHelper()
    test_a.build_query(results_to_get=v, table_name=table_source,
                       search_data=table_col, data=id_pro, operator='compare')
    res2 = test_a.unit_dict()
    print(res2)
#     pg = pg.SqlHelper()
#     PGClass()
#     pg2 = pg.SqlHelper()
#     pg2 = PGClass.SqlHelper()
#     pg.build_query(results_to_get=v, table_name=table_source,
#                    search_data=table_data, data=value, operator='end')
#
#     pg2.build_query(results_to_get=v, table_name=table_source,
#                     search_data=table_col, data=id_pro, operator='compare')
#
    test_a = SqlHelper()
#     test_b = SqlHelper()
#     test_a.build_query(results_to_get=v, table_name=table_source,
#                        search_data=table_data, data=value, operator='end')
#     test_b.build_query(results_to_get=v, table_name=table_source,
#                        search_data=table_col, data=id_pro, operator='compare')
#
#     pg.order_by_asc("product_name")
#     res_a = test_a.unit_dict()
#     res_b = test_b.execute_all()
#
#     res_pg = pg.unit_dict()
#     res_pg2 = pg2.execute_all()
#
#     test_a.order_by_asc("product_name")
#     res_a = test_a.unit_dict()
#     res_b = test_b.execute_all()
#     print(res_a)
#     print(res_b)
#
#     print(res_pg)
#     print(res_pg2)
#
# # operator = ('compare', 'start', 'end', 'have')
# # select a from b where c OPERTOR D
