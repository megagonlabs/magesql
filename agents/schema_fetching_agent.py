"""
Schema Provider Agent (currently only for Spider Dataset)
"""

import sys
import os
import logging
import json
from pathlib import Path

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .base_agent import BaseAgent
from dataset_classes.spider_dataset import SpiderDataset
from dataset_classes.wikisql_dataset import WikiSQLDataset
from utils.sql_utils import get_sql_for_database

schema_fetching_properties = {
    'name': 'SchemaFetchingAgent',
    'description': 'Get database schema given database name and path',
    'input': 'database name and database dir path',
    'output': 'database schema text'
}

class SchemaFetchingAgent(BaseAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = schema_fetching_properties['name']
        super().__init__(**kwargs)

        self.description = schema_fetching_properties['description']
        self.input = schema_fetching_properties['input']
        self.output = schema_fetching_properties['output']

        self.schema = None ## db_id to schema text mapping
        if 'cache_schema_path' in kwargs and kwargs['cache_schema_path']:
            print(f"Loading schema cache from {kwargs['cache_schema_path']}")
            self.schema = self._load_schema(kwargs['cache_schema_path'])
        else:
            cache_schema_path = os.path.join('../', os.path.dirname(__file__), '../datasets', 'spider', 'db_id2schema_text.json')
            ## create the cache directory if not exists
            Path(os.path.dirname(cache_schema_path)).mkdir(parents=True, exist_ok=True)
            print(f"Computing schema cache..")
            if 'dataset_path' not in kwargs or not kwargs['dataset_path']:
                kwargs['dataset_path'] = os.path.join('../', os.path.dirname(__file__), '../datasets', 'spider')
            self.schema = self._compute_schema(kwargs['dataset_path'])
            with open(cache_schema_path, 'w') as f:
                json.dump(self.schema, f, indent=4)
            print(f"Schema cache saved to {cache_schema_path}")
        pass

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)


    def _initialize_properties(self):
        super()._initialize_properties()
        for key in schema_fetching_properties:
            self.properties[key] = schema_fetching_properties[key]

    def _load_schema(self, schema_path:str):
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        return schema
    
    def _compute_schema(self, dataset_path:str):
        """
        A quick implementation of reusing existing database class to get db schema. Can be optimized further.
        """
        if not dataset_path:
            dataset_name = "spider"
            dataset_path = os.path.join('../', os.path.dirname(__file__), '../datasets', dataset_name)
        dataset = SpiderDataset(dataset_path)
        split_names = ['train', 'dev', 'test']
        schema = {}
        for split_name in split_names:
            for record in dataset.data[split_name]:
                db_id = record['db_id']
                db_path = record['db_path'] ## the sqlite db file path
                if db_id not in schema:
                    table_schemas = get_sql_for_database(db_path)
                    schema[db_id] = table_schemas
        print(f"Schema cache computed for {len(schema)} databases")
        return schema

    def format_output(self, output_dict:dict):
        pass
    
    def format_schema(self, table_schemas, separator:str="\n\n"):
        if not table_schemas:
            return None
        schema_text = separator.join(table_schemas)
        return schema_text

    def run(self, db_id:str):
        if db_id not in self.schema:
            print(f"Schema information not found for db_id {db_id}")
            return None
        return self.format_schema(self.schema[db_id])


def test_agent():
    agent = SchemaFetchingAgent()
    print("Agent properties:")
    print(agent.properties)

    db_id = 'concert_singer'
    schema_text = agent.run(db_id)
    print(f"Schema text for {db_id}:")
    print(schema_text)

if __name__ == '__main__':
    test_agent()
