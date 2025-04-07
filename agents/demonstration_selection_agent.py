"""
Database Routing Agent (currently only for Spider Dataset)
Currently hardness and struct selectors are not supported.
"""

import sys
import os
import sqlite3
import logging

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import torch
from nltk.tokenize import word_tokenize

from .base_agent import BaseAgent
from dataset_classes.spider_dataset import SpiderDataset
from dataset_classes.wikisql_dataset import WikiSQLDataset
from utils.database_routing_utils import load_model, predict_db
from utils.construct_prompt_utils import fill_demonstrations

from demonstration_selector.first_k_demonstration_selector import FirstKDemonstrationSelector
from demonstration_selector.random_demonstration_selector import RandomDemonstrationSelector
from demonstration_selector.hardness_demonstration_selector import HardnessDemonstrationSelector
from demonstration_selector.jac_demonstration_selector import JacDemonstrationSelector
from demonstration_selector.struct_demonstration_selector import StructDemonstrationSelector

demonstration_selection_agent_properties = {
    'name': 'DemonstrationSelectionAgent',
    'description': 'Provide demonstrations for natural language questions',
    'input': 'natual language question in dataset',
    'output': 'demonstrations in list of str format for in context learning'
}

class DemonstrationSelectionAgent(BaseAgent):
    def __init__(self, dataset=None, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = demonstration_selection_agent_properties['name']
        super().__init__(**kwargs)

        self.description = demonstration_selection_agent_properties['description']
        self.input = demonstration_selection_agent_properties['input']
        self.output = demonstration_selection_agent_properties['output']
        
        self.dataset = dataset
        self.demonstration_selector = JacDemonstrationSelector(self.dataset) ## default demonstration selector
        

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)


    def _initialize_properties(self):
        super()._initialize_properties()
        for key in demonstration_selection_agent_properties:
            self.properties[key] = demonstration_selection_agent_properties[key]

    def initialize_demonstration_selector(self, demonstration_selector_option:str='jaccard'):
        if demonstration_selector_option == 'first_k':
            demonstration_selector = FirstKDemonstrationSelector(self.dataset)
        elif demonstration_selector_option == 'random':
            demonstration_selector = RandomDemonstrationSelector(self.dataset)
        # elif demonstration_selector_option == 'hardness':
            # demonstration_selector = HardnessDemonstrationSelector(self.dataset)
        elif demonstration_selector_option == 'jaccard':
            demonstration_selector = JacDemonstrationSelector(self.dataset)
        # elif demonstration_selector_option == 'struct':
        #     demonstration_selector = StructDemonstrationSelector(self.dataset)
        else:
            raise ValueError(f"Invalid demonstration selector: {demonstration_selector_option}")
        return demonstration_selector

    def get_data_dict(self, question_text:str):
        data_dict = {
            'question': question_text,
            'question_toks': word_tokenize(question_text)
        }
        return data_dict
    
    def format_output(self, demonstrations):

        pass

    def run(self, question:str, demonstration_selector_option:str='jaccard', num_demonstrations:int=5):
        if self.demonstration_selector is None or self.demonstration_selector.name != f'{demonstration_selector_option}_demonstration_selector':
            ## swtich to a new demonstration selector
            self.demonstration_selector = self.initialize_demonstration_selector(demonstration_selector_option)
        demonstrations = self.demonstration_selector.select_demonstrations(
            self.get_data_dict(question),
            num_demonstrations=num_demonstrations,
            flag_return_ids = False
        )
        template = "### Answer the following question: {question}\n{sql_query}"

        ## convert demonstrations in dataset format to demonstrations in list of (question, query) format
        demonstrations = [(x['question'], x['query']) for x in demonstrations]
        demonstration_section_text = fill_demonstrations(demonstrations, template)
        return demonstration_section_text


def test_agent():
    from agents.data_loader_agent import DataLoaderAgent
    data_loader_agent = DataLoaderAgent()
    dataset_name = "spider"
    dataset_dir_path = os.path.join('../', os.path.dirname(__file__), '../datasets', dataset_name)
    dataset = data_loader_agent.run(dataset_name, dataset_dir_path)

    agent = DemonstrationSelectionAgent(dataset=dataset)
    print("Agent properties:")
    print(agent.properties)

    question = "How many singers are there?"
    response = agent.run(question)
    print(f"Question: {question}")
    print(f"Demonstrations:\n{response}")

if __name__ == '__main__':
    test_agent()
