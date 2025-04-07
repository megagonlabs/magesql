import tiktoken

PROMPT_TEMPLATE = {
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

def count_tokens(text, tokenizer=None):
    if tokenizer is None:
        tokenizer = tiktoken.get_encoding("cl100k_base")
    return len(tokenizer.encode(text))

def format_demonstration(question, query, single_demo_template=None):
    """Convert a demonstration to text.
    """
    if not single_demo_template:
        single_demo_template = "### Answer the following question: {}\n{}"
    return single_demo_template.format(question, query)


def fill_demonstrations_with_structed_template(demonstrations:list, template:dict=None, remaining_tokens:int=4096):
    """Given the content and template to fill, fill the demonstration section. Re-use the template dictionary. Need to make the template as str and independent from the template dict.
    """
    if not template:
        template = PROMPT_TEMPLATE
    if "demonstration_section" in template:
        template = template["demonstration_section"]
    res = {
        "prefix": template["prefix"],
        "demonstrations": None,
        "suffix": template["suffix"],
    }
    sep = template["seperator"]
    fixed_tokens = 0
    prefix = template["prefix"]
    if prefix != None:
        res["prefix"] = prefix
        fixed_tokens += count_tokens(res["prefix"])
    suffix = template["suffix"]
    if suffix != None:
        res["suffix"] = suffix
        fixed_tokens += count_tokens(res["suffix"])
    ## count tokens of seperator (before & after demonstration body)
    fixed_tokens += (int(prefix is not None) + int(suffix is not None)) * count_tokens(sep)
    if fixed_tokens >= remaining_tokens:
        print(f"There is no space to fill even one demonstration. Current fix tokens for prefix and suffix: {fixed_tokens}, remaining tokens for demonstration section: {remaining_tokens}")
    demonstration_texts = []
    used_tokens = fixed_tokens
    for demo in demonstrations:
        formatted_demo = format_demonstration(demo[0], demo[1])
        demo_tokens = count_tokens(formatted_demo) + count_tokens(sep)
        if used_tokens + demo_tokens > remaining_tokens:
            break
        demonstration_texts.append(formatted_demo)
        used_tokens += demo_tokens
    res["demonstrations"] = sep.join(demonstration_texts)
    section_text = sep.join([x for x in res.values() if x is not None])
    return section_text


def fill_demonstrations(demonstrations:list, template:str=None, sep:str='\n\n', remaining_tokens:int=4096):
    """Given the content and template to fill, fill the demonstration section. Re-use the template dictionary. Need to make the template as str and independent from the template dict.
    """
    if not template:
        template = "### Answer the following question: {question}\n{sql_query}"
    if remaining_tokens < 1:
        print(f"There is no space to fill even one demonstration. remaining tokens for demonstration section: {remaining_tokens}")
        return ""
    filled_demos = []
    used_tokens = 0
    sep_tokens = count_tokens(sep) 
    for demo in demonstrations:
        question, sql_query = demo[0], demo[1]
        demo_str = template.format(question=question, sql_query=sql_query)
        demo_tokens = count_tokens(demo_str)
        if used_tokens + demo_tokens + len(filled_demos)*sep_tokens > remaining_tokens:
            break
        else:
            filled_demos.append(demo_str)
            used_tokens += demo_tokens

    return sep.join(filled_demos) if filled_demos else ""


def get_prompt_construction_template(template_option:str='option_1'):
    if template_option == 'option_1':
        template = """### Complete sqlite SQL query only and with no explanation.\n\n{demonstration_text}{schema_text}### Answer the following question: {question}"""
    elif template_option == 'option_2':
        template = """/* Complete sqlite SQL query only and with no explanation.*/\n\n:{demonstration_text}{schema_text}### Answer the following question: {question}"""
    elif template_option == 'option_3':
        template = """/* Some example questions and corresponding SQL queries are provided based on similar problems: */:\n\n{demonstration_text}{schema_text}"""
    else:
        raise ValueError(f"Invalid template option: {template_option}")
    return template

def fill_prompt_construction_prompt(question:str, schema_text:str=None, demonstration_text:str=None ,template_option:str='option_1'):
    """
    Currently assume the demonstration_text already contains the prefix. Need to update the template if in future demonstration_text does not contain the prefix.
    """
    if template_option == 'option_1':
        demonstration_text = '' if not demonstration_text else f"### Some example pairs of question and corresponding SQL query are provided based on similar problems:\n\n{demonstration_text}\n\n"
        schema_text = '' if not schema_text else f"### Given the following database schema:\n{schema_text}\n\n"
        template = """### Complete sqlite SQL query only and with no explanation.\n\n{demonstration_text}{schema_text}### Answer the following question: {question}"""
    elif template_option == 'option_2':
        demonstration_text = '' if not demonstration_text else f"/* Some example pairs of question and corresponding SQL query are provided based on similar problems: */:\n\n{demonstration_text}\n\n"
        schema_text = '' if not schema_text else f"/* Given the following database schema: */:\n{schema_text}\n\n"
        template = """/* Complete sqlite SQL query only and with no explanation.*/\n\n{demonstration_text}{schema_text}/* Answer the following: {question} */\nSELECT """
    elif template_option == 'option_3':
        demonstration_text = '' if not demonstration_text else f"/* Some example pairs of question and corresponding SQL query are provided based on similar problems: */:\n\n{demonstration_text}\n\n"
        schema_text = '' if not schema_text else f"/* Given the following database schema: */:\n{schema_text}\n\n"
        template = """{demonstration_text}{schema_text}/* Answer the following: {question} */\nSELECT """
    output = template.format(question=question, schema_text=schema_text, demonstration_text=demonstration_text)
    return output

