import psycopg2
from server_automation.configuration import config
import logging


# Read me SqlHelper class can execute Sql statement in 2 ways
# 1.0v by Shay Perpinial
# send to constructor of class Host , DataBase, User, Pass, scheme ,  port,
# From the object can produce with build_query , sending the parameters by
#       - "results_to_get" = Select  can get None as a default and get all the parameters as *
#       - "table_name" = From The table that get the data from as format  "SchemasName".TableName
#       - "search_data" = The data that we compare to column name .
#       - "data" = Columns  name from the table that we compare to the Data
#       - "operator" =  there is 4  operator available  = ('compare', 'start', 'end', 'have')  send a string of the
#                       desire operation start/ end  "Like" operation for start with and ending string .
#       - "as_dict" = Boolean flag to get the results as a dictionary OBJ

#     Sending Sql statement with static method, without create OBJ or parameters  and get result.

# If you prefer to receive an object in the form of a value / key dictionary as a return.
# You can add the dict_of_table function as an additional function to the SqlHelper object

#

class SqlHelper:
    def __init__(self, host=config.PG_HOST, database=config.PG_JOB_TASK_DB_NAME, user=config.PG_USER,
                 password=config.PG_PASS, scheme=config.SCHEMA_RASTER_CATALOG_MANAGER, port=5432):
        self.table = None
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.scheme = scheme
        self.query = str()  # The string that will execute the query
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port)
        except Exception as e:
            raise ConnectionError(f'Error on connection to DB with error: {str(e)}')

    def build_query(self, results_to_get, table_name, search_data, data, operator, as_dict=False):
        self.table = table_name
        condition = []
        value = results_to_get if results_to_get is not None else '*'
        self.query = f"""SELECT {value} FROM {table_name} WHERE """
        condition.append(search_data)
        condition.append(data)
        self.query += self.__operation(operator, condition)
        print(self.query)

    def __compare(self, var_condition):
        condition = f"{var_condition[0]} = '{var_condition[1]}'"
        return condition

    def __start_with(self, var_condition):
        statement = f""""{var_condition[0]}" LIKE '{var_condition[1]}%'"""
        return statement

    def __end_with(self, var_condition):
        statement = f"{var_condition[0]} LIKE '%{var_condition[1]}'"
        return statement

    def __have_in_query(self, var_condition):
        statement = f"{var_condition[0]} LIKE '%{var_condition[1]}%' "
        return statement

    def execute_one(self):
        try:
            cur = self.conn.cursor()
            cur.execute(self.query)
        except Exception as e:
            logging.exception(e)

        return cur.fetchone()

    def execute_all(self):
        try:
            cur = self.conn.cursor()
            cur.execute(self.query)
        except Exception as e:
            logging.exception(e)

        return cur.fetchall()

    # Function to decide each operator use on the statement
    def __operation(self, op, condition):
        operation_dict = {'compare': self.__compare(condition),
                          'start': self.__start_with(condition),
                          'end': self.__end_with(condition),
                          'have': self.__have_in_query(condition)
                          }
        return operation_dict[op]

    def order_by_desc(self, variable):  # default
        self.query += f" ORDER BY {variable} DESC"

    def order_by_asc(self, variable):
        self.query += f" ORDER BY {variable} ASC"

    def unit_dict(self):
        res = self._list_of_column()
        query_list = self.execute_one()
        return dict(zip(res, query_list))

    def _list_of_column(self):
        cur = self.conn.cursor()
        sql = f"""SELECT * FROM {self.table} """
        cur.execute(sql)
        column_names = [desc[0] for desc in cur.description]
        print(column_names)
        self.conn.commit()
#       self.conn.close()
        return column_names

    def execute_sql_statement(self, query):

        try:
            cur = self.conn.cursor()
            cur.execute(query)
        except Exception as e:
            logging.exception(e)
        return cur.fetchall()








