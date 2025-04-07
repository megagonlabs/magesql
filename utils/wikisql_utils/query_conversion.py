import re

import records
from babel.numbers import parse_decimal, NumberFormatError
 
from .query import Query

schema_re = re.compile(r'\((.+)\)')
num_re = re.compile(r'[-+]?\d*\.\d+|\d+')


agg_ops = ['', 'MAX', 'MIN', 'COUNT', 'SUM', 'AVG']
cond_ops = ['=', '>', '<', 'OP']
syms = ['SELECT', 'WHERE', 'AND', 'COL', 'TABLE', 'CAPTION', 'PAGE', 'SECTION', 'OP', 'COND', 'QUESTION', 'AGG', 'AGGOPS', 'CONDOPS']

def get_schema(cls, db, table_id):
        table_infos = db.query('SELECT sql from sqlite_master WHERE tbl_name = :name', name=cls.get_id(table_id)).all()
        if table_infos:
            return table_infos[0]
        else:
            return None
    
def get_schema_for_table(table_id, db_path=None, db_conn=None, flag_truncate=True):
    close_in_func = False
    if db_conn is None:
        db = records.Database('sqlite:///{}'.format(db_path))
        db_conn = db.get_connection()
        close_in_func = True
    
    # query_res = db_conn.query('SELECT sql FROM sqlite_master WHERE tbl_name = :table_name', table_name=table_id).all()
    table_info = db_conn.query('SELECT sql from sqlite_master WHERE tbl_name = :name', name=table_id).all()[0].sql
    if flag_truncate:
        schema_str = schema_re.findall(table_info)[0]
    else:
        schema_str = table_info

    if close_in_func:
        db_conn.close()

    return schema_str


def execute_query_by_records(query, where_map=None, db_path=None, db_conn=None):
    close_in_func = False
    if db_conn is None:
        db = records.Database('sqlite:///{}'.format(db_path))
        db_conn = db.get_connection()
        close_in_func = True
    if where_map is None:
        res = db_conn.query(query)
    else:
        res = db_conn.query(query, **where_map)
    query_res = [o.result for o in res]
    # print("Processed query:", query_res)
    if close_in_func:
        db_conn.close()
    return query_res
    

def get_schema_col2type(table_id, db_path=None, db_conn=None):
    schema_str = get_schema_for_table(table_id, db_path, db_conn)
    schema = {}
    for tup in schema_str.split(', '):
        c, t = tup.split()
        schema[c] = t
    return schema

def get_schema_str(table_id, db_path=None, db_conn=None, col2text=None):
    schema_str = get_schema_for_table(table_id, db_path, db_conn, flag_truncate=False)
    ## replace col{x} with text in col2text
    if col2text:
        for col, text in col2text.items():
            schema_str = schema_str.replace(col, f'"{text}"')
    return schema_str
    # schema_idx2text = {}
    # for col, text in col2text.items():
    #     schema_idx2text[col] = text
    # return schema_idx2text

def proc_col_name(col_name):
    # Regular expression pattern to match whitespace or special characters
    whitespace_or_special_chars_pattern = re.compile(r'[^\w\s]')

    # Check if col_name contains whitespace or special characters
    if whitespace_or_special_chars_pattern.search(col_name):
        if col_name.startswith('"') and col_name.endswith('"'):
            # Return col_name as is if it is already enclosed in double quotes
            return col_name
        # Enclose col_name in double quotes if it contains whitespace or special characters
        return '"{}"'.format(col_name)
    else:
        # Return col_name as is if it doesn't contain whitespace or special characters
        return col_name

def proc_table_id(table_id):
    return 'table_{}'.format(table_id.replace('-', '_')) if not table_id.startswith('table') else table_id

def fix_quote_in_query_value(sql_query):
    def replace_quotes(match):
        # Replace single quotes within the string literal with two single quotes ('')
        return match.group(0).replace("'", "''")

    # Regular expression pattern to match string literals enclosed in either single or double quotes
    string_literal_pattern = r'(["\'])(.*?)\1'

    # Replace each matched string literal with its modified version
    return re.sub(string_literal_pattern, replace_quotes, sql_query)

def convert_query_dict_to_sql(table_id, query:Query, lower=True, db_path=None, db_conn=None, col2type=None, col2text=None):
    # get necessary information from the query
    try:
        select_index, aggregation_index, conditions = query.sel_index, query.agg_index, query.conditions
    except AttributeError:
        raise ValueError('query must be a Query object containing sel_index, agg_index, and conditions attributes')

    if not table_id.startswith('table'):
        table_id = 'table_{}'.format(table_id.replace('-', '_'))
    
    # schema_str = get_schema_for_table(table_id, db_path, db_conn)
    # schema = {}
    # for tup in schema_str.split(', '):
    #     c, t = tup.split()
    #     schema[c] = t
    if col2type is None:
        col2type = get_schema_col2type(table_id, db_path=db_path, db_conn=db_conn)
    # schema_idx2text = {}

    # if col2text:
    #     for col, text in col2text.items():
    #         schema_idx2text[col] = text

    select = 'col{}'.format(select_index)
    if col2text:
        select = col2text[select]
        select = proc_col_name(select)
        
    agg = Query.agg_ops[aggregation_index]
    if agg:
        select = '{}({})'.format(agg, select)

    where_clause = []
    where_map = {}
    for col_index, op, val in conditions:
        if lower and isinstance(val, str):
            val = val.lower()
        if col2type.get('col{}'.format(col_index)) == 'real' and not isinstance(val, (int, float)):
            try:
                val = float(parse_decimal(val))
            except NumberFormatError as e:
                val = float(num_re.findall(val)[0])
        if col2text:
            col_val = col2text.get('col{}'.format(col_index), None)
            val = "'{}'".format(val) if isinstance(val, str) else val  # Quote string values
            where_clause.append('{} {} {}'.format(proc_col_name(col_val), Query.cond_ops[op], val))
        else:
            where_clause.append('col{} {} :col{}'.format(col_index, Query.cond_ops[op], col_index))
        where_map['col{}'.format(col_index)] = val

    where_str = 'WHERE {}'.format(' AND '.join(where_clause)) if where_clause else ''

    query = 'SELECT {} AS result FROM {} {}'.format(select, table_id, where_str)

    # if col2text:
    #     query_res = execute_query_by_records(query, None, db_path, db_conn)
    # else:
    #     query_res = execute_query_by_records(query, where_map, db_path, db_conn)
    return query


def convert_sql_to_query_dict(sql, headers):
    # Regular expressions for parsing SQL
    select_re = re.compile(r"SELECT\s+(\w+)\((\w+)\)\s+FROM", re.IGNORECASE)
    where_re = re.compile(r"WHERE\s+(\w+)\s*([=><])\s*'([^']+)'", re.IGNORECASE)

    # Predefined mappings
    agg_ops = ['', 'MAX', 'MIN', 'COUNT', 'SUM', 'AVG']
    cond_ops = ['=', '>', '<']

    # Find selected column and aggregation
    select_match = select_re.search(sql)
    agg, sel_col = select_match.groups() if select_match else ('', '')
    sel_index = headers.index(sel_col) if sel_col in headers else -1
    agg_index = agg_ops.index(agg.upper()) if agg.upper() in agg_ops else 0

    # Parse conditions
    conditions = []
    for match in where_re.finditer(sql):
        col, op, val = match.groups()
        if col in headers:
            col_index = headers.index(col)
            op_index = cond_ops.index(op) if op in cond_ops else -1
            conditions.append([col_index, op_index, val])

    # Return the structured Query
    return Query(sel_index, agg_index, conditions)