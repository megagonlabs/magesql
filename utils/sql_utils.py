from typing import Iterable
import re
import os
import argparse

import sqlite3

def execute_query(queries, db_path=None, curr_cursor=None):
    """Run queries on the database, and return the results.
    The queries can be a single query or a batch of queries. List of results will be return if the input is the latter case.
    """
    if db_path is None:
        raise ValueError("the database path cannot be None")
    
    flag_close_cursor = False
    if curr_cursor is None:
        ## create a new db connection if current cursor is None
        db_conn = sqlite3.connect(db_path)
        curr_cursor = db_conn.cursor()
        flag_close_cursor = True
    
    if isinstance(queries, str):
        ## excute single query
        res = curr_cursor.execute(queries).fetchall()
    elif isinstance(queries, Iterable):
        ## excute multiple query if the input is an iterable
        res = [curr_cursor.execute(x).fetchall() for x in queries]
    else:
        raise TypeError(f"queries cannot be {type(queries)}")
    
    if flag_close_cursor:
        curr_cursor.close()
        db_conn.close()
    return res


def get_table_names(db_path=None, curr_cursor=None):
    """From Dail-SQL
    """
    table_names = execute_query(queries="SELECT name FROM sqlite_master WHERE type='table'", db_path=db_path, curr_cursor=curr_cursor)
    table_names = [_[0] for _ in table_names]
    return table_names


def get_sql_for_database(db_path=None, curr_cursor=None):
    """From Dail-SQL
    """
    close_in_func = False
    if curr_cursor is None:
        con = sqlite3.connect(db_path)
        curr_cursor = con.cursor()
        close_in_func = True

    table_names = get_table_names(db_path, curr_cursor)

    queries = [f"SELECT sql FROM sqlite_master WHERE tbl_name='{name}'" for name in table_names]

    sqls = execute_query(queries, db_path, curr_cursor)

    if close_in_func:
        curr_cursor.close()

    return [_[0][0] for _ in sqls]


"""
From C3 & test-suite-sql-eval
"""
def replace_cur_year(query: str) -> str:
    ## this is the preprocessing step in test-suite-sql-eval
    return re.sub(
        r"YEAR\s*\(\s*CURDATE\s*\(\s*\)\s*\)\s*", "2020", query, flags=re.IGNORECASE
    )


def get_cursor_from_path(sqlite_path: str):
    try:
        if not os.path.exists(sqlite_path):
            print("Openning a new connection %s" % sqlite_path)
        connection = sqlite3.connect(sqlite_path)
    except Exception as e:
        print(sqlite_path)
        raise e
    connection.text_factory = lambda b: b.decode(errors="ignore")
    cursor = connection.cursor()
    return cursor


def exec_on_db_(sqlite_path: str, query: str, flag_replace_cur_year=True):
    if flag_replace_cur_year:
        query = replace_cur_year(query)
    cursor = get_cursor_from_path(sqlite_path)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        cursor.connection.close()
        return "result", result
    except Exception as e:
        cursor.close()
        cursor.connection.close()
        return "exception", e


def is_valid(sql, db_path):
    flag, _ = exec_on_db_(db_path, sql)
    if flag == "exception":
        return 0
    else:
        return 1
    

def postprocess(query: str) -> str:
    query = query.replace('> =', '>=').replace('< =', '<=').replace('! =', '!=')
    return query


def get_exec_result_from_query(sql, db_path, flag_postprocess=True):
    """return the execution result of the input SQL query on the database at db_path
    flag: 'result' or 'exception'
    results: list of tuples format
    """
    if flag_postprocess:
        sql = postprocess(sql)
    flag, result = exec_on_db_(db_path, sql)
    if flag == "exception":
        return flag, result
    return flag, result
    

def exec_on_db_return_columns(sqlite_path: str, query: str, flag_replace_cur_year=True):
    if flag_replace_cur_year:
        query = replace_cur_year(query)
    cursor = get_cursor_from_path(sqlite_path)
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        result = cursor.fetchall()
        cursor.close()
        cursor.connection.close()
        return "result", result, columns
    except Exception as e:
        cursor.close()
        cursor.connection.close()
        return "exception", e, None
    
def get_exec_result_from_query_return_columns(sql, db_path, flag_postprocess=True):
    """return the execution result of the input SQL query on the database at db_path
    flag: 'result' or 'exception'
    results: list of tuples format
    """
    if flag_postprocess:
        sql = postprocess(sql)
    flag, result, columns = exec_on_db_return_columns(db_path, sql)
    if flag == "exception":
        return flag, result, None
    return flag, result, columns
    
