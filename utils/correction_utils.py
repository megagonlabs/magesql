import pandas as pd
from typing import List, Union, Optional

def find_foreign_keys_MYSQL_like(db_name, spider_foreign):
    """Generate the foreign keys for self-correction.
    """
    df = spider_foreign[spider_foreign['Database name'] == db_name]
    output = "["
    for _, row in df.iterrows():
        output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row['Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
    output= output[:-1] + "]"
    return output

def find_fields_MYSQL_like(db_name, spider_schema):
    """Generate the fields for self-correction.
    """
    df = spider_schema[spider_schema['Database name'] == db_name]
    df = df.groupby(' Table Name')
    output = ""
    for name, group in df:
        output += "Table " +name+ ', columns = ['
        for _, row in group.iterrows():
            output += row[" Field Name"]+','
        output = output[:-1]
        output += "]\n"
    return output

def find_primary_keys_MYSQL_like(db_name, spider_primary):
    """Generate the primary keys for self-correction.
    """
    df = spider_primary[spider_primary['Database name'] == db_name]
    output = "["
    for _, row in df.iterrows():
        output += row['Table Name'] + '.' + row['Primary Key'] +','
    output = output[:-1]
    output += "]\n"
    return output

def creating_schema(DATASET_JSON):
    """Generate the schema for self-correction.
    """
    schema_df = pd.read_json(DATASET_JSON)
    schema_df = schema_df.drop(['column_names','table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index == -1:
                for table in tables:
                    schema.append([row['db_id'], table, '*', 'text'])
            else:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in primary_keys:
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
    spider_schema = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
    spider_primary = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    spider_foreign = pd.DataFrame(f_keys, columns=['Database name', 'First Table Name', 'Second Table Name', 'First Table Foreign Key', 'Second Table Foreign Key'])
    return spider_schema, spider_primary, spider_foreign


def generate_instruction(rules_groups=[1,2,3], flag_add_generic_rules=False):
    """Generate the instruction for self-correction. User could add rules in this function."""
    # if rules_groups is not list but integer, then convert integer to list
    if isinstance(rules_groups, int):
        rules_groups = [rules_groups]
    query = [] if not flag_add_generic_rules else generic_instruction()
    query.append("#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.\n")
    query.append("#### Use the following instructions for fixing the SQL QUERY:\n")
    ## TDOD: add more rules & add options to select which rules to use
    group2rules = {
        ## rules group 1
        1: [
            "Use the db_name values that are explicitly mentioned in the question.",
            "Pay attention to the columns that are used for the JOIN by using the Foreign_keys.",
            "Use DESC and DISTINCT when needed.",
            "Pay attention to the columns that are used for the GROUP BY statement.",
            "Pay attention to the columns that are used for the SELECT statement.",
            "Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).",
            "Use GROUP BY on one column only.",
        ],
        ## rules group 2
        2: [
            "When the question only asks for a certain field, please don't include the COUNT(*) in the SELECT statement, but instead use it in the ORDER BY clause to sort the results based on the count of that field.",
            """Please don't use "IN", "OR", "LEFT JOIN" as it might cause extra results, use "INTERSECT" or "EXCEPT" instead, and remember to use "DISTINCT" or "LIMIT" when necessary.""",
        ],
        ## rules group 3
        3: [
            "Don't make error that write queries with multiple join operations as one with nested subqueries with IN keyword, please use join to get correct results in such cases.",
            "Please think when to use conjunction, sometimes you may need to use conjunction to get correct results.",
        ],
        ## rules group 4
        4: [
            "When the question only asks for a certain field, please don't include the COUNT(*) in the SELECT statement, but instead use it in the ORDER BY clause to sort the results based on the count of that field.",
            """Please don't use "IN", "LEFT JOIN" as it might cause extra results, use "INTERSECT" or "EXCEPT" instead, and remember to use "DISTINCT" or "LIMIT" when necessary.""",
        ],
    }
    rules = []
    for group in rules_groups:
        if group in group2rules:
            rules.extend(group2rules[group])
    for i, rule in enumerate(rules):
        query.append(str(i+1) + ") " + rule + '\n')
    query = "".join(query)
    query += '\n'
    return query

def generate_instruction_wikisql(rules_groups=[1], flag_add_generic_rules=False):
    # if rules_groups is not list but integer, then convert integer to list
    if isinstance(rules_groups, int):
        rules_groups = [rules_groups]
    """Generate the instruction for self-correction. User could add rules in this function."""
    query = [] if not flag_add_generic_rules else generic_instruction()
    query.append("#### For the given question, use the provided table schema to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.\n")
    query.append("#### Use the following instructions for fixing the SQL QUERY:\n")
    ## TDOD: add more rules & add options to select which rules to use
    group2rules = {
        ## rules group 1
        1: [
            """Here are the SQL operations allowed :\naggregation operaters: 'MAX', 'MIN', 'COUNT', 'SUM', 'AVG'; comparison operators: '=', '>', '<'; symbols: 'SELECT', 'WHERE', 'AND', 'COL', 'TABLE'""",
            """Please be careful that the generated SQL will be executed directly with python sqlite3 library, so please correct the SQL to be compatible with sqlite3, i.e. single quote inside of string that need to be matched should be escaped by another single quote, and the column name should be wrapped by double quote.""",
        ]
    }
    rules = []
    for group in rules_groups:
        if group in group2rules:
            rules.extend(group2rules[group])
    for i, rule in enumerate(rules):
        query.append(str(i+1) + ") " + rule + '\n')
    query = "".join(query)
    query += '\n'
    return query

def generic_instruction():
    rules = [
        "#### Take a deep breath and think step by step. I need you to fix the SQL to make the system work if there is any problems in it. Please provide the SQL back in full because I have no fingers. If you do a good job I'll tip you $200."
        "#### I know it's a hard task but you can do it! I believe in you!"
    ]
    return rules

def geneerate_instruction_with_given_rules_text(rules_text):
    query = []
    query += "#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.\n"
    query += "#### Use the following instructions for fixing the SQL QUERY:\n"
    query += rules_text
    query += '\n'
    return query

def construct_self_correction_prompt(test_sample_text, db_name, sql, spider_schema, spider_primary, spider_foreign, rules_groups=[1,2,3], flag_add_generic_rules=False):
    instruction = generate_instruction(rules_groups=rules_groups, flag_add_generic_rules=flag_add_generic_rules)
    fields = find_fields_MYSQL_like(db_name, spider_schema)
    fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(db_name, spider_foreign) + '\n'
    fields += "Primary_keys = " + find_primary_keys_MYSQL_like(db_name, spider_primary)
    prompt = instruction + fields+ '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY\nSELECT'
    return prompt


def construct_self_correction_prompt_wikisql(question, table_schema, prev_query, rules_groups=[1], flag_add_generic_rules=False):
    instruction = generate_instruction_wikisql(rules_groups=rules_groups, flag_add_generic_rules=flag_add_generic_rules)
    fields = '#### Table Schema:\n' + table_schema + '\n'
    prompt = instruction + fields + '#### Question: ' + question + '\n#### SQLite SQL QUERY\n' + prev_query +'\n#### SQLite FIXED SQL QUERY\nSELECT'
    return prompt


def fill_error_correction_prompt(question:str, sql_query:str, schema_text:str=None, rules_groups=Union[List[int], str], template:str=None):
    instruction = generate_instruction(rules_groups=rules_groups) if not isinstance(rules_groups, str) else geneerate_instruction_with_given_rules_text(rules_groups)
    schema_text = '' if not schema_text else f"#### Table Schema:\n{schema_text}\n\n"
    if not template:
        template = f"""{instruction}{schema_text}#### Question:\n{question}\n#### SQLite SQL QUERY:\n{sql_query}\n\n#### SQLite FIXED SQL QUERY\nSELECT"""
    output = template.format(schema_text=schema_text, question=question, sql_query=sql_query)
    return output
