"""
Error Correction Agent
"""

import sys
import os
import sqlite3
import logging
from typing import List
from openai import OpenAI

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .base_agent import BaseAgent
from dataset_classes.spider_dataset import SpiderDataset
from dataset_classes.wikisql_dataset import WikiSQLDataset
from utils.construct_prompt_utils import fill_prompt_construction_prompt
from utils.openai_utils import init_openai_client, get_prompt_from_openai
from utils.correction_utils import fill_error_correction_prompt
from utils.sql_str_utils import query_postprocessing

error_correction_properties = {
    'name': 'ErrorCorrectionAgent',
    'description': 'Correct the SQL query by re-prompting',
    'input': 'natural language question, previous generated SQL query, database schema',
    'output': 'corrected SQL query'
}

class ErrorCorrectionAgent(BaseAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = error_correction_properties['name']
        super().__init__(**kwargs)

        self.description = error_correction_properties['description']
        self.input = error_correction_properties['input']
        self.output = error_correction_properties['output']
        openai_api_key = kwargs.get('openai_api_key', None)
        openai_organization = kwargs.get('openai_organization', '')
        self._initialize_openai_client(openai_api_key, openai_organization)


    def _initialize(self, properties=None):
        super()._initialize(properties=properties)


    def _initialize_properties(self):
        super()._initialize_properties()
        for key in error_correction_properties:
            self.properties[key] = error_correction_properties[key]

    def _initialize_openai_client(self, openai_api_key:str, openai_organization:str=''):
        self.client = init_openai_client(openai_api_key, openai_organization)

    def prompt_openai(self, prompt_text:str, model:str='gpt-4', temperature:float=0.0, n:int=1, seed:int=None):
        res = get_prompt_from_openai(
            self.client,
            model=model,
            data=prompt_text,
            temperature=temperature,
            n=n,
            seed=seed,
            max_num_retry=5,
            flag_use_original=True,
            flag_return_text_only=True
        )
        return res

    def format_output(self, output_dict:dict):
        pass

    def run(self, question:str, sql_query:str, schema_text:str=None, rules_groups:List[int]=[1,3,4], model:str='gpt-4'):
        prompt_text = fill_error_correction_prompt(
            question, 
            sql_query, 
            schema_text,
            rules_groups=rules_groups
        )
        if prompt_text is None:
            print("Prompt text is None, cannot construct prompt.")
            return None
        prompt_res = self.prompt_openai(prompt_text, model=model)
        prompt_res = query_postprocessing(prompt_res)
        return prompt_text, prompt_res
    
    def run_with_generated_prompt(self, prompt_text:str, model:str='gpt-4'):
        prompt_res = self.prompt_openai(prompt_text, model=model)
        prompt_res = query_postprocessing(prompt_res)
        return prompt_text, prompt_res


def test_agent():
    from agents.data_loader_agent import DataLoaderAgent
    from agents.database_routing_agent import DatabaseRoutingAgent
    from agents.demonstration_selection_agent import DemonstrationSelectionAgent
    from agents.schema_fetching_agent import SchemaFetchingAgent
    from agents.prompt_construction_agent import PromptConstructionAgent
    
    print("======== Test Prompt Construction Agent:")
    agent = ErrorCorrectionAgent()
    print("Agent properties:")
    print(agent.properties)

    print("==== Test Data Loader Agent:")
    data_loader_agent = DataLoaderAgent()
    dataset_name = "spider"
    dataset_dir_path = os.path.join('../', os.path.dirname(__file__), '../datasets', dataset_name)
    dataset = data_loader_agent.run(dataset_name, dataset_dir_path)
    record_idx = 16
    print(f"try to get one record in dev split with record_idx {record_idx}")
    record = dataset.data['dev'][16]
    print(record)
    print("Data loader agent tested successfully.\n")

    print("==== Test Database Routing Agent:")
    model_path = './database_routing/saved_models/database_routing_spider_v1'
    database_routing_agent = DatabaseRoutingAgent(model_path=model_path)
    question = record['question']
    db_id = database_routing_agent.run(question)
    print(f"Database id for question: {question} is {db_id}, the ground truth db_id is {record['db_id']}")
    if db_id == record['db_id']:
        print("Database routing successful find the correct database.")
    else:
        print("Database routing failed to find the correct database.")
    print("Database routing agent tested successfully.\n")
    
    print("==== Test Demonstration Selection Agent:")
    demonstration_selection_agent = DemonstrationSelectionAgent(dataset=dataset)
    demontration_text = demonstration_selection_agent.run(question, demonstration_selector_option='jaccard', num_demonstrations=5)
    print(f"Demonstrations in text format:\n{demontration_text}")

    print("==== Test Schema Fetching Agent:")
    schema_file_path = './datasets/spider/db_id2schema_text.json'
    schema_fetching_agent = SchemaFetchingAgent(cache_schema_path=schema_file_path)
    schema_text = schema_fetching_agent.run(db_id)
    print(f"Schema text for db_id {db_id}:\n{schema_text}")

    print("==== Test Prompt Construction Agent:")
    prompt_construction_agent = PromptConstructionAgent()
    prompt_text, prompt_res = prompt_construction_agent.run(question, schema_text, demontration_text)
    print(f"Prompt text:\n{prompt_text}")
    print(f"Prompt result:\n{prompt_res}")

    print("=== Test Error Correction Agent:")
    prompt_text, prompt_res = agent.run(question, schema_text, demontration_text)
    print(f"Prompt result:\n{prompt_res}")
    print(f"Error correction prompt text:\n{prompt_text}")
    print(f"Error correction prompt result:\n{prompt_res}")

    print("Prompt Construction Agent tested successfully.\n")
    

if __name__ == '__main__':
    test_agent()
