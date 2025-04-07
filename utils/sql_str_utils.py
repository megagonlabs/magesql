import re


def replace_cur_year(query: str) -> str:
    return re.sub(
        "YEAR\s*\(\s*CURDATE\s*\(\s*\)\s*\)\s*", "2020", query, flags=re.IGNORECASE
    )

def query_preprocessing(sql:str):
    """
    Preprocess the generated SQL query
    """
    sql = " ".join(sql.replace("\n", " ").split())
    sql = sql.strip().split("/*")[0]
    if sql.startswith("SELECT"):
        return sql + "\n"
    elif sql.startswith(" "):
        return "SELECT" + sql + "\n"
    else:
        return "SELECT " + sql + "\n"

def query_postprocessing(sql:str):
    """
    Postprocess the generated SQL query
    """
    sql = " ".join(sql.replace("\n", " ").split())
    sql = sql.strip().split("/*")[0]
    if sql.startswith("SELECT"):
        return sql + "\n"
    elif sql.startswith(" "):
        return "SELECT" + sql + "\n"
    else:
        return "SELECT " + sql + "\n"