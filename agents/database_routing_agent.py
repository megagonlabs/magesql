"""
Database Routing Agent (currently only for Spider Dataset)
"""

import sys
import os
import sqlite3
import logging

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import torch

from .base_agent import BaseAgent
from dataset_classes.spider_dataset import SpiderDataset
from dataset_classes.wikisql_dataset import WikiSQLDataset
from utils.database_routing_utils import load_model, predict_db

database_routing_properties = {
    'name': 'DatabaseRoutingAgent',
    'description': 'Predict the database id for a given question',
    'input': 'natual language question',
    'output': 'database id'
}

class DatabaseRoutingAgent(BaseAgent):
    def __init__(self, model_path=None, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = database_routing_properties['name']
        super().__init__(**kwargs)

        self.description = database_routing_properties['description']
        self.input = database_routing_properties['input']
        self.output = database_routing_properties['output']
        
        self.model_path = model_path
        try:
            self.model, self.tokenizer, self.label_map = load_model(model_path)
        except Exception as e:
            raise ValueError(f"Error loading model at path {model_path}: {e}")
        
        ## load schema if provided
        if 'schema_path' in kwargs and kwargs['schema_path']:
            self.schema = self._load_schema(kwargs['schema_path'])


    def _initialize(self, properties=None):
        super()._initialize(properties=properties)


    def _initialize_properties(self):
        super()._initialize_properties()
        for key in database_routing_properties:
            self.properties[key] = database_routing_properties[key]

    def _load_schema(self, schema_path:str):
        pass

    def get_schema_text(self, db_id:str):
        pass

    def format_output(self, output_dict:dict):
        pass

    def run(self, question:str, flag_return_schema_text:bool=False):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        db_id = predict_db(
            model=self.model,
            tokenizer=self.tokenizer,
            text=question,
            device=device,
            label_map=self.label_map
        )
        if flag_return_schema_text:
            return self.get_schema_text(db_id)
        return db_id


def test_agent():
    model_path = './database_routing/saved_models/database_routing_spider_v1'
    agent = DatabaseRoutingAgent(model_path=model_path)
    print("Agent properties:")
    print(agent.properties)

    question = "How many singers are there?"
    db_id = agent.run(question)
    print(f"Question: {question}")
    print(f"Predicted db_id: {db_id}")

if __name__ == '__main__':
    test_agent()
