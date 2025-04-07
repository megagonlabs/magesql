import os
from copy import deepcopy
import json
from tqdm import tqdm

from nltk.tokenize import word_tokenize
import records

from dataset_classes.base_dataset import BaseDataset
# from .base_dataset import BaseDataset
from utils.dataset_utils import load_json_records, load_txt_records, load_line_by_line_json

from utils.wikisql_utils.query import Query
from utils.wikisql_utils.query_conversion import get_schema_for_table, get_schema_col2type, convert_query_dict_to_sql, get_schema_str, proc_table_id

class WikiSQLDataset(BaseDataset):
    dataset_name = "wikisql"

    train_file_name = "data/train.jsonl"
    train_sql_file_name = ""
    train_database_dir_name = "data/train.db"
    train_table_schema_file_name = "data/train.tables.jsonl"

    dev_file_name = "data/dev.jsonl"
    dev_sql_file_name = ""
    dev_database_dir_name = "data/dev.db"
    dev_table_schema_file_name = "data/dev.tables.jsonl"

    test_file_name = "data/test.jsonl"
    test_sql_file_name = ""
    test_database_dir_name = "data/test.db"
    test_table_schema_file_name = "data/test.tables.jsonl"


    def assign_idx_to_record(self):
        """Add one additional key "id" with index of record in the split
        """
        for split_name in self.data.keys():
            for i, record in enumerate(self.data[split_name]):
                record['idx'] = i
        return
    
    def add_database_path(self):
        """Store the database path in each record
        """
        for split_name in self.data.keys():
            for record in self.data[split_name]:
                ## database dir path according to the split train dev and test
                database_dir_path = ""
                if split_name == 'train':
                    database_dir_path = self.train_database_dir_path
                elif split_name == 'dev':
                    database_dir_path = self.dev_database_dir_path
                elif split_name == 'test':
                    database_dir_path = self.test_database_dir_path
                db_path = database_dir_path
                record['db_path'] = db_path
        return

    def tokenize_questions(self):
        """Tokenize the questions. Tokenization results are already stored in the dataset file.
        """
        pass

    def tokenize_queries(self):
        """Tokenize the SQL queries. Tokenization results are already stored in the dataset file.
        """
        pass

    def load_schema(self, external_schema_cache:str=None, flag_overwrite:bool=False):
        if external_schema_cache and os.path.exists(external_schema_cache):
            with open(external_schema_cache, 'r') as f:
                self.schema = json.load(f)
            print(f"Schema cache loaded from {external_schema_cache}")
            return
        split_names = ['train', 'dev', 'test']
        for split_name, table_schema_path in zip(split_names, [self.train_table_schema_path, self.dev_table_schema_path, self.test_table_schema_path]):
            db_path = self.get_db_path(split_name)
            # db_conn = records.Database('sqlite:///{}'.format(db_path)) ## will have cocurrent bottleneck issue
            schema_list = load_line_by_line_json(table_schema_path) # table_id, header, types, row_count
            print(f"Loaded schema for {split_name} split: {len(schema_list)} tables.")
            self.schema[split_name] = dict()
            for schema_dict in tqdm(schema_list):
                schema_dict['table_id'] = proc_table_id(schema_dict['id'])
                table_id = schema_dict['table_id']
                schema_dict['text2col'] = {col_name: f"col{idx}" for idx, col_name in enumerate(schema_dict['header'])}
                schema_dict['col2text'] = {f"col{idx}": col_name for idx, col_name in enumerate(schema_dict['header'])}
                ## get schema string
                schema_dict['schema_str'] = get_schema_str(
                    schema_dict['table_id'], 
                    db_path=db_path,
                    # db_conn=db_conn, 
                    col2text={f"col{idx}": col_name for idx, col_name in enumerate(schema_dict['header'])}
                ) 
                ## get col to data type mapping
                schema_dict['col2type'] = get_schema_col2type(table_id, db_path=db_path)
                self.schema[split_name][table_id] = schema_dict

        ## store schema in cache
        if flag_overwrite or not os.path.exists(external_schema_cache):
            with open(external_schema_cache, 'w') as f:
                json.dump(self.schema, f)
            print(f"Schema cache saved to {external_schema_cache}")
        # db_conn.close()

    def load_splits(self, external_schema_cache:str=None):
        """Load the train and test splits
        """
        # self.train_data = load_json_records(self.train_file_path)
        split_names = ['train', 'dev', 'test']
        for split_name, file_path in zip(split_names, [self.train_file_path, self.dev_file_path, self.test_file_path]):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found.")
            db_path = self.get_db_path(split_name)
            self.data[split_name] = load_line_by_line_json(file_path) # phase, sql, question, table_id
            print(f"Loaded {split_name} split: {len(self.data[split_name])} records.")

            ## get query string
            for record in self.data[split_name]:
                record['table_id'] = proc_table_id(record['table_id'])
                record['db_id'] = split_name
                table_id = record['table_id']
                schema_dict = self.schema[split_name][table_id]
                record['query_dict'] = record['sql'].copy()
                query_sql = convert_query_dict_to_sql(
                    record['table_id'], 
                    Query.from_dict(record['query_dict']),
                    db_path=db_path,
                    # db_conn=db_conn,
                    col2text=schema_dict['col2text'],
                    col2type=schema_dict['col2type']
                )
                # query_sql = Query.from_dict(query_dict)
                record['query'] = query_sql
                record['question_toks'] = word_tokenize(record['question'])
                record['query_toks'] = None
            # db_conn.close()
            print(f"Loaded {len(self.data[split_name])} records for {split_name} split.")
        return
    
    def get_db_path(self, split_name):
        """Get the database path for the given split
        """
        if split_name == 'train':
            return self.train_database_dir_path
        elif split_name == 'dev':
            return self.dev_database_dir_path
        elif split_name == 'test':
            return self.test_database_dir_path
        else:
            raise ValueError(f"Invalid split name {split_name}")

    # def inject_schema_into_instance(self):
    #     """Inject the schema into each instance
    #     """
    #     for split_name in self.data.keys():
    #         for record in self.data[split_name]:
    #             table_id = record['table_id']
    #             db_path = self.get_db_path(split_name)
    #             schema = get_schema_dict(table_id, db_path=db_path, db_conn=None)
    #             record['schema'] = schema
    #             pass
    #     return
    
    def load_data(self):
        """Load the whole dataset
        """
        schema_cache_path = os.path.join(self.dataset_dir_path, "schema_cache.json")
        self.load_schema(schema_cache_path)
        self.load_splits()
        self.assign_idx_to_record()
        self.tokenize_questions()
        self.tokenize_queries()
        self.add_database_path()
        print("Dataset loaded.")
        return
    
