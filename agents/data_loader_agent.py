"""
Data Loader Agent (currently only for Spider Dataset)
"""

import sys
import os
import sqlite3
import logging

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .base_agent import BaseAgent
from dataset_classes.spider_dataset import SpiderDataset
from dataset_classes.wikisql_dataset import WikiSQLDataset

data_loader_properties = {
    'name': 'DataLoaderAgent',
    'description': 'Load NL2SQL database',
    'input': 'dataset name and dataset dir path',
    'output': 'dataset class instance'
}

class DataLoaderAgent(BaseAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = data_loader_properties['name']
        super().__init__(**kwargs)

        self.description = data_loader_properties['description']
        self.input = data_loader_properties['input']
        self.output = data_loader_properties['output']
        

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)


    def _initialize_properties(self):
        super()._initialize_properties()
        for key in data_loader_properties:
            self.properties[key] = data_loader_properties[key]


    def format_output(self, output_dict:dict):
        pass

    def run(self, dataset_name='spider', dataset_dir_path:str=None):
        ## if the dataset_dir_path is not provided, use the default path datasets/{dataset_name}
        if not dataset_dir_path:
            dataset_dir_path = os.path.join('../', os.path.dirname(__file__), 'datasets', dataset_name)
        if dataset_name == 'spider':
            dataset = SpiderDataset(dataset_dir_path)
        elif dataset_name == 'WikiSQL':
            dataset = WikiSQLDataset(dataset_dir_path)
        else:
            raise ValueError(f"Invalid dataset name {dataset_name}")
        dataset.load_schema()
        return dataset
    


def test_agent():
    agent = DataLoaderAgent()
    print("Agent properties:")
    print(agent.properties)

    # Example dataset loading for spider dataset
    dataset_name = "spider"
    dataset_dir_path = os.path.join('../', os.path.dirname(__file__), '../datasets', dataset_name)
    dataset = agent.run(dataset_name, dataset_dir_path)

    print("First record in train split:")
    print(dataset.data['train'][0])
    print("First record in dev split:")
    print(dataset.data['dev'][0])
    print("First record in test split:")
    print(dataset.data['test'][0])
    

if __name__ == '__main__':
    test_agent()
