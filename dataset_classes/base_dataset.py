import os
import json
from abc import abstractmethod

from utils.dataset_utils import load_json_records, load_txt_records

class BaseDataset(object):
    def __init__(self, dataset_dir_path):
        self.name = self.dataset_name
        self.dataset_dir_path = dataset_dir_path

        self.train_file_path = os.path.join(dataset_dir_path, self.train_file_name)
        self.train_sql_file_path = os.path.join(dataset_dir_path, self.train_sql_file_name)
        self.train_database_dir_path = os.path.join(dataset_dir_path, self.train_database_dir_name)
        self.train_table_schema_path = os.path.join(dataset_dir_path, self.train_table_schema_file_name)

        self.dev_file_path = os.path.join(dataset_dir_path, self.dev_file_name)
        self.dev_sql_file_path = os.path.join(dataset_dir_path, self.dev_sql_file_name)
        self.dev_database_dir_path = os.path.join(dataset_dir_path, self.dev_database_dir_name)
        self.dev_table_schema_path = os.path.join(dataset_dir_path, self.dev_table_schema_file_name)

        self.test_file_path = os.path.join(dataset_dir_path, self.test_file_name)
        self.test_sql_file_path = os.path.join(dataset_dir_path, self.test_sql_file_name)
        self.test_database_dir_path = os.path.join(dataset_dir_path, self.test_database_dir_name)
        self.test_table_schema_path = os.path.join(dataset_dir_path, self.test_table_schema_file_name)

        self.data = dict() # store the records of each split
        self.db = dict() # store the databases, not used currently
        self.schema = dict() # store the schema, not used currently
        self.load_data()
    
    @abstractmethod
    def load_data(cls):
        """Load the whole dataset
        """
        raise NotImplementedError

    @abstractmethod
    def tokenize_questions(cls):
        """generate the tokenization results of input NL questions.
        """
        pass
    
    @abstractmethod
    def tokenize_queries(self):
        """generate the tokenization results of input NL SQL.
        """
        pass

    @abstractmethod
    def get_sql_tree(cls):
        """for each SQL in the training set, obtain its parsed format as a labeled tree.
        """
        pass

    @abstractmethod
    def get_sql_sketch(cls):
        """for each NL question, obtain a SQL sketch/clause of it.
        """
        pass