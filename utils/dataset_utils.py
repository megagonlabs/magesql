"""
Utils for datasets
"""

import json
import os
from pathlib import Path


def load_json_records(file_path:str):
    """Load records from a json file
    """
    with open(file_path, 'r') as f:
        records = json.load(f)
    return records

def load_txt_records(file_path:str):
    """Load records from a line by line txt file
    """
    with open(file_path, 'r') as f:
        records = [line.strip() for line in f.readlines()]
    return records

def save_line_by_line_json(data, file_path:str):
    """Save a data into line by line json format
    """
    # create directory if not exists
    Path.mkdir(Path(file_path).parent, parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')

def load_line_by_line_json(file_path:str):
    """Load the data from a line by line json file
    """
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data