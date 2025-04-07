"""
SQL Execution Agent (currently only for Spider Dataset)
"""

import sys
import os
import sqlite3
import logging

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .base_agent import BaseAgent
from utils.sql_utils import get_exec_result_from_query, get_exec_result_from_query_return_columns
from dataset_classes.spider_dataset import SpiderDataset

sql_execution_properties = {
    'name': 'SQLExecutionAgent',
    'description': 'Execute SQL queries on Sqlite database',
    'input': 'SQL query and database id',
    'output': 'records in json format'
}

class SqlExecutionAgent(BaseAgent):
    def __init__(self, database_path:str=None, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = sql_execution_properties['name']
        super().__init__(**kwargs)

        self.description = sql_execution_properties['description']
        self.input = sql_execution_properties['input']
        self.output = sql_execution_properties['output']
        self.database_path = database_path
        ## optional: check if the database path exists
        if not os.path.exists(database_path) and not os.path.isfile(database_path):
            raise FileNotFoundError(f"Database path {database_path} not found.")
    
    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in sql_execution_properties:
            self.properties[key] = sql_execution_properties[key]


    def format_output(self, output_dict:dict):
        """Format the output dictionary into a readable string.
        """
        if output_dict["query_exec_flag"] != "error":
            if "query_exec_columns" in output_dict:
                ## convert to list of dict
                columns = output_dict["query_exec_columns"]
                results = output_dict["query_exec_result"]
                output_dict["query_exec_result"] = [{col_name: value for col_name, value in zip(columns, row_tuple)} for row_tuple in results]
            else:
                ## convert list of tuple to list of list
                output_dict["query_exec_result"] =  [list(row_tuple) for row_tuple in output_dict["query_exec_result"]]
    
    def error_handling(self, result:dict):
        if result["query_exec_flag"] != "error":
            return result
        exec_result = result["query_exec_result"]
        if isinstance(exec_result, Exception):
            error_type = type(exec_result).__name__
            error_message = f"{error_type}: {exec_result.args[0]}"  # Use the exception's class name and the first argument (error message)
        else:
            # In case it's not an exception, just convert it to string
            error_message = f"Error: {str(exec_result)}"
        result = {"status": "error", "error_message": error_message}
        return result

    def run(self, sql_query:str, database:str, database_path:str=None, return_col_names=True) -> dict:
        """
        Executes an SQL query on the specified database and returns the result.
        
        Parameters:
        sql_query (str): The SQL query to execute.
        database (str): The Name/ID of the database to run the query on.
        database_path (str): The path to the directory containing the database files.
        return_col_names (bool): Whether to return the column names along with the query results.
        
        Returns:
        dict: A dictionary containing query results or errors.
        """
        if database_path is None:
            database_path = self.database_path
        db_path = os.path.join(database_path, database, f"{database}.sqlite") # Spider dataset
        
        print(f"Executing query on database {database} at {db_path}")
        print(f"SQL Query: {sql_query}")
        
        try:
            if return_col_names:
                flag, result, columns = get_exec_result_from_query_return_columns(sql_query, db_path)
            else:
                flag, result = get_exec_result_from_query(sql_query, db_path)
            
            flag = "error" if flag == "exception" else flag ## rename the flag
        except Exception as e:
            raise Exception(f"Exception during SQL execution: {e}")
        output_dict = {
            "query_exec_flag": flag, 
            "query_exec_result": result
        }
        if return_col_names:
            output_dict["query_exec_columns"] = columns
        self.format_output(output_dict)
        if output_dict["query_exec_flag"] == "error":
            return self.error_handling(output_dict)
        return output_dict
    
