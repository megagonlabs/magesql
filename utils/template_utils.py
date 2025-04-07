import os

import tiktoken
import sqlite3

from utils.sql_utils import get_sql_for_database
from utils.correction_utils import creating_schema

TEMPLATE = {
    "instruction_section": "",
    "demonstration_section": {
        "prefix": "",
        "each_demonstration": "",
        "suffix": "",
        "seperator": "\n\n",
    },
    "question_section": {
        "prefix": "",
        "schema": "",
        "body": "",
        "suffix": "SELECT ",
        "seperator": "\n\n",
    },
    "section_seperator": "\n\n",
    "max_tokens": 4096
}

def count_tokens(text, tokenizer=None):
    if tokenizer is None:
        tokenizer = tiktoken.get_encoding("cl100k_base")
    return len(tokenizer.encode(text))

def get_template(template_option):
    if template_option == 'template_option_1':
        template = {
            "instruction_section": "### Complete sqlite SQL query only and with no explanation.",
            "demonstration_section": {
                "prefix": "### Some example pairs of question and corresponding SQL query are provided based on similar problems:",
                "each_demonstration": "### Answer the following question: {}\n{}",
                "suffix": None,
                "seperator": "\n\n",
            },
            "question_section": {
                "prefix": "### Given the following database schema:",
                "schema": "from_query_on_db",
                "body": "### Answer the following question: {}",
                "suffix": "SELECT ",
                "seperator": "\n\n"
            },
            "section_seperator": "\n\n",
            "max_tokens": 4096
        }
    elif template_option == 'template_option_2':
        template = {
            "instruction_section": "/* Complete sqlite SQL query only and with no explanation.*/",
            "demonstration_section": {
                "prefix": "/* Some example questions and corresponding SQL queries are provided based on similar problems: */",
                "each_demonstration": "/* Answer the following: {}*/\n{}",
                "suffix": None,
                "seperator": "\n\n",
            },
            "question_section": {
                "prefix": "/* Given the following database schema: */",
                "schema": "from_query_on_db",
                "body": "/* Answer the following: {}*/\nSELECT ",
                "suffix": None,
                "seperator": "\n\n",
            },
            "section_seperator": "\n\n",
            "max_tokens": 4096
        }
    elif template_option == 'template_option_3':
        template = {
            "instruction_section": None,
            "demonstration_section": {
                "prefix": "/* Some example questions and corresponding SQL queries are provided based on similar problems: */",
                "each_demonstration": "/* Answer the following: {}*/\n{}",
                "suffix": None,
                "seperator": "\n\n",
            },
            "question_section": {
                "prefix": "/* Given the following database schema: */",
                "schema": "from_query_on_db",
                "body": "/* Answer the following: {}*/\nSELECT ",
                "suffix": None,
                "seperator": "\n\n",
            },
            "section_seperator": "\n\n",
            "max_tokens": 4096
        }
    else:
        raise ValueError(f"template option {template_option} is not supported.")
    return template


def extract_create_statements(schema_sql_file_path:str):
    """Extract the create statements from the sql file.
    """
    with open(schema_sql_file_path, 'r') as file:
        lines = file.readlines()

    create_statements = []
    capture = False
    current_statement = ""

    for line in lines:
        if line.strip().upper().startswith('CREATE TABLE'):
            capture = True
            current_statement = line
        elif capture and ';' in line:
            current_statement += line
            create_statements.append(current_statement.strip().rstrip('\n'))
            capture = False
            current_statement = ""
        elif capture:
            current_statement += line

    return create_statements


def get_schema_text_from_schema_sql_file(db_path:str, separator:str="\n\n"):
    """Given the content, return the schema section.
    """
    # schema_sql_file_path = os.path.join(db_path, 'schema.sql')
    schema_sql_file_path = db_path
    table_schemas = extract_create_statements(schema_sql_file_path)
    if not table_schemas:
        return None
    schema_text = separator.join(table_schemas)
    return schema_text


def get_schema_text_from_query_on_db(db_path:str, separator:str="\n\n"):
    table_schemas = get_sql_for_database(db_path)
    if not table_schemas:
        return None
    schema_text = separator.join(table_schemas)
    return schema_text

def get_schema_text_from_wikisql_dataset(dataset):
    return None


def fill_schema(content_dict:dict, template:dict):
    """Given the content and template to fill, fill the schema sub-section in question section.
    """
    schema_option = template["question_section"].get("schema", None)
    if not schema_option:
        # skip schema part
        return None
    elif schema_option == "from_schema_sql_file":
        ## assume db_schema_path is already in data
        ## currently have issue on spider dataset because some database does not have schema.sql or <db_id>.sql file
        return get_schema_text_from_schema_sql_file(content_dict["db_schema_path"])
    elif schema_option == "from_query_on_db":
        return get_schema_text_from_query_on_db(content_dict["db_path"])
    else:
        raise ValueError(f"schema option {schema_option} is not supported.")
    

def fill_question(content_dict:dict, template:dict):
    """Given the content and template to fill, fill the question section in question section.
    """
    pass

def format_demonstration(content_dict:dict, template:dict):
    """Convert a demonstration to text.
    """
    return template["demonstration_section"]["each_demonstration"].format(content_dict["question"], content_dict["query"])


def fill_demonstrations(content_dict:dict, template:dict, remaining_tokens:int=4096):
    """Given the content and template to fill, fill the demonstration section.
    """
    if not template["demonstration_section"]:
        return
    res = {
        "prefix": template["demonstration_section"]["prefix"],
        "demonstrations": None,
        "suffix": template["demonstration_section"]["suffix"],
    }
    sep = template["demonstration_section"]["seperator"]
    fixed_tokens = 0
    prefix = template["demonstration_section"]["prefix"]
    if prefix != None:
        res["prefix"] = prefix
        fixed_tokens += count_tokens(res["prefix"])
    suffix = template["demonstration_section"]["suffix"]
    if suffix != None:
        res["suffix"] = suffix.format(content_dict["question"])
        fixed_tokens += count_tokens(res["suffix"])
    ## count tokens of seperator (before & after demonstration body)
    fixed_tokens += (int(prefix is not None) + int(suffix is not None)) * count_tokens(sep)
    if fixed_tokens >= remaining_tokens:
        print(f"There is no space to fill even one demonstration. Current fix tokens for prefix and suffix: {fixed_tokens}, remaining tokens for demonstration section: {remaining_tokens}")
    ## join demonstrations to text
    ## TODO: strategy to select demonstrations within valid tokens range
    demonstrations = sep.join(format_demonstration(x, template) for x in content_dict["demonstrations"])
    res["demonstrations"] = demonstrations
    section_text = sep.join([x for x in res.values() if x is not None])
    return section_text


def fill_question_body(content_dict:dict, template:dict):
    """Given the content and template to fill, fill the question body in question section.
    """
    return template["question_section"]["body"].format(content_dict["question"])


def fill_question_section(content_dict:dict, template:dict, remaining_tokens:int=4096, provided_schema:str=None):
    separator = template["question_section"]["seperator"]
    question_texts = []
    if template["question_section"].get("prefix", None):
        question_texts.append(template["question_section"]["prefix"])
    if template["question_section"].get("schema", None):
        if provided_schema is not None:
            question_texts.append(provided_schema)
        else:
            question_texts.append(fill_schema(content_dict, template))
    if template["question_section"].get("body", None):
        question_texts.append(fill_question_body(content_dict, template))
    if template["question_section"].get("suffix", None):
        question_texts.append(template["question_section"]["suffix"])
    res = separator.join(question_texts)
    num_tokens = count_tokens(res)
    if num_tokens >= remaining_tokens:
        print(f"There is no space to fill question section. Current tokens: {num_tokens}, remaining tokens for question section: {remaining_tokens}")
    return res
    
def fill_template(content_dict:dict, template:str, valid_sections=None, tokenizer=None, provided_schema=None):
    if tokenizer is None:
        tokenizer = tiktoken.get_encoding("cl100k_base")
    
    if valid_sections is None:
        valid_sections = ["instruction_section", "demonstration_section", "question_section"]

    section2text = {key: None for key in valid_sections}

    max_tokens = template["max_tokens"]
    num_valid_section = 0
    num_tokens = 0
    if "instruction_section" in section2text:
        instruction_section_text = template["instruction_section"]
        section2text["instruction_section"] = instruction_section_text
        if instruction_section_text is not None:
            num_valid_section += 1
            num_tokens += count_tokens(instruction_section_text)
    if "question_section" in section2text:
        question_section_text = fill_question_section(content_dict, template, max_tokens-num_tokens, provided_schema=provided_schema)
        section2text["question_section"] = question_section_text
        if question_section_text is not None:
            num_valid_section += 1
            num_tokens += count_tokens(question_section_text)
    num_tokens += max(num_valid_section-1, 0) * count_tokens(template["section_seperator"])
    if "demonstration_section" in section2text:
        demonstration_section_text = fill_demonstrations(content_dict, template, max_tokens-num_tokens)
        section2text["demonstration_section"] = demonstration_section_text
        if demonstration_section_text is not None:
            num_valid_section += 1
            num_tokens += count_tokens(demonstration_section_text)
    section_seperator = template["section_seperator"]
    output_text = section_seperator.join([section2text[x] for x in valid_sections if section2text[x] is not None])
    total_tokens = count_tokens(output_text)
    assert total_tokens <= max_tokens, f"total tokens {total_tokens} exceeds the maximum tokens {max_tokens}"
    return output_text, total_tokens