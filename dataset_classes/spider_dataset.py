import os
import json

from dataset_classes.base_dataset import BaseDataset
# from .base_dataset import BaseDataset
from utils.dataset_utils import load_json_records, load_txt_records

class SpiderDataset(BaseDataset):
    dataset_name = "spider"

    train_file_name = "train_spider_and_others.json"
    train_sql_file_name = "train_gold.sql"
    train_database_dir_name = "database"
    train_table_schema_file_name = "tables.json"

    dev_file_name = "dev.json"
    dev_sql_file_name = "dev_gold.sql"  # please replace with your own generated SQL queries if you need
    dev_database_dir_name = "database"
    dev_table_schema_file_name = "tables.json"

    test_file_name = "test.json"
    test_sql_file_name = "test_gold.sql"  # please replace with your own generated SQL queries if you need
    test_database_dir_name = "test_database" # there are individual databases for test split
    test_table_schema_file_name = "test_tables.json" # there are individual databases for test split

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
        self.db_paths = dict()
        for split_name in self.data.keys():
            self.db_paths[split_name] = dict()
            for record in self.data[split_name]:
                ## database dir path according to the split train dev and test
                database_dir_path = ""
                if split_name == 'train':
                    database_dir_path = self.train_database_dir_path
                elif split_name == 'dev':
                    database_dir_path = self.dev_database_dir_path
                elif split_name == 'test':
                    database_dir_path = self.test_database_dir_path
                else:
                    raise ValueError(f"Invalid split name {split_name}")
                # db_path = os.path.join(self.database_dir_path, record['db_id'])
                db_path = os.path.join(database_dir_path, record['db_id'], record['db_id']+'.sqlite')
                record['db_path'] = db_path
                self.db_paths[split_name][record['db_id']] = db_path
                ## check if there is a file named "schema.sql" in the db_path, if not, check <db_id>.sql, if also not, raise error
                # db_schema_path = os.path.join(db_path, "schema.sql")
                # if os.path.exists(db_schema_path):
                #     record['db_schema_path'] = db_schema_path
                # elif os.path.exists(os.path.join(db_path, record['db_id'] + ".sql")):
                #     record['db_schema_path'] = os.path.join(db_path, record['db_id'] + ".sql")
                # else:
                #     raise FileNotFoundError(f"Database schema file not found for {record['db_id']}")
        return

    def tokenize_questions(self):
        """Tokenize the questions. Tokenization results are already stored in the dataset file.
        """
        pass

    def tokenize_queries(self):
        """Tokenize the SQL queries. Tokenization results are already stored in the dataset file.
        """
        pass

    def load_splits(self):
        """Load the train and test splits
        """
        # self.train_data = load_json_records(self.train_file_path)
        split_names = ['train', 'dev', 'test']
        for split_name, file_path, file_sql_path in zip(split_names, [self.train_file_path, self.dev_file_path, self.test_file_path], [self.train_sql_file_path, self.dev_sql_file_path, self.test_sql_file_path]):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found.")
            self.data[split_name] = load_json_records(file_path)
            ## Optional: load the gold SQL queries, but spider dataset already has the SQL queries in the split file
            # gold_sql = load_txt_records(file_sql_path)
            # for record, sql in zip(self.data[split_name], gold_sql):
            #     record['query'] = sql
            print(f"Loaded {len(self.data[split_name])} records for {split_name} split.")
        return
    
    def load_data(self):
        """Load the whole dataset
        """
        self.load_splits()
        self.assign_idx_to_record()
        self.tokenize_questions()
        self.tokenize_queries()
        self.add_database_path()
        print("Dataset loaded.")
        return
    
    def load_schema(self):
        """Load the table schema for the dataset
        """
        self.table_schema = dict()
        self.table_schema['train'] = self.load_schema_file(self.train_table_schema_path)
        self.table_schema['dev'] = self.load_schema_file(self.dev_table_schema_path)
        self.table_schema['test'] = self.load_schema_file(self.test_table_schema_path)
        return
    
    def load_schema_file(self, schema_file_path):
        """Load the table schema for the dataset
        """
        with open(schema_file_path, 'r') as f:
            table_schema = json.load(f)
        ## change list of tables to dict of tables
        table_schema = {table['db_id']: table for table in table_schema}
        print(f"Loaded table schema for {len(table_schema)} tables.")
        return table_schema
    