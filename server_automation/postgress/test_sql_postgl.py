# By Shay perpinial not to GIT . LOCAL CHECK.

from server_automation.postgress.sql_helper import SqlHelper


def sql_main():
    table_data = 'product_name'
    value = '_ayosh_10cm'
    id_pro = "2022_09_04T10_03_43Z_MAS_6_ORT_247557"
    table_col = "product_id"
    table_source = '"RasterCatalogManager".records'
    v = None

    test_a = SqlHelper()
    test_b = SqlHelper()
    test_a.build_query(results_to_get=v, table_name=table_source,
                       search_data=table_data, data=value, operator='end')
    test_b.build_query(results_to_get=v, table_name=table_source,
                       search_data=table_col, data=id_pro, operator='compare')

    test_a.order_by_asc("product_name")
    res_a = test_a.unit_dict()
    res_b = test_b.execute_all()
    print(res_a)
    print(res_b)

# operator = ('compare', 'start', 'end', 'have')
# select a from b where c OPERTOR D
