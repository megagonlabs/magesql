import sys
import os

from fastapi import FastAPI,  HTTPException 
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic import BaseModel
from typing import List, Dict, Optional

# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# from agent_center import AgentCenter  # Import the updated AgentCenter class
# from gold_sql_retrieval import GoldSQLRetrieval

from .agent_center import AgentCenter  # Import the updated AgentCenter class
from .gold_sql_retrieval import GoldSQLRetrieval

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize FastAPI app and AgentCenter
app = FastAPI()

# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change "*" to specific domains if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

agent_center = AgentCenter()

dataset_dir_path = "./datasets/spider"
pairs_cache_path = os.path.join(dataset_dir_path, 'question2sql.json')
embeddings_cache_path = os.path.join(dataset_dir_path, 'question_embeddings.pt')
gold_sql_retrieval = GoldSQLRetrieval(
    dataset_dir_path,
    pairs_cache_path=pairs_cache_path,
    embeddings_cache_path=embeddings_cache_path
)

# Define request models
class AgentToggleRequest(BaseModel):
    agent_name: str
    status: str  # This is the status ("active" or "inactive")

class RunPipelineRequest(BaseModel):
    question: str
    flag_use_database_routing_agent: bool = False
    db_id: Optional[str] = None 
    flag_use_demonstration_selection_agent: bool = False
    num_demonstrations: int = 5
    prompt_template: str = "template1"
    model:str = "gpt-4"
    flag_use_error_correction_agent: bool = False
    flag_use_sql_execution_agent: bool = False

class SQLExecutionRequest(BaseModel):
    sql_query: str
    db_id: str

class FetchSchemaRequest(BaseModel):
    db_id: str

class SelectDemonstrationsRequest(BaseModel):
    question: str
    num_demonstrations: int

class ConstructPromptRequest(BaseModel):
    question: str
    demonstration_text: str
    schema_text: str

class ApplyErrorCorrectionRequest(BaseModel):
    question: str
    sql_query: str
    schema_text: str

class GoldSQLRetrievalRequest(BaseModel):
    question: str

class ExecutePromptConstructionAgentRequest(BaseModel):
    question: str
    schema_text: str
    demonstration_text: str
    template_option: str
    model: str

class ExecuteErrorCorrectionAgentRequest(BaseModel):
    question: str
    sql_query: str
    schema_text: str
    rules_groups: List[int]
    model: str

class ExecuteErrorCorrectionAgentWithGeneratedPromptRequest(BaseModel):
    prompt_text: str
    model: str

class ExecuteDemonstrationSelectionAgentRequest(BaseModel):
    question: str
    # demonstration_selector_option: str
    num_demonstrations: int

class ExecuteDatabaseRoutingAgentRequest(BaseModel):
    question: str


# 1. Get Agent Statuses
@app.get("/agents")
async def get_agent_statuses():
    """
    Return the current activation status of all agents.
    """
    return agent_center.agent_name2status

# 2. Toggle Agent Activation Status
@app.post("/agents/toggle")
async def toggle_agent_status(request: AgentToggleRequest):
    """
    Toggle the activation status of a specific agent.
    """
    try:
        logging.debug(f"Received request: {request}")
        agent_name = request.agent_name
        status = request.status  # "active" or "inactive"
        new_status = agent_center.toggle_agent_status(agent_name, status)
        if new_status != status:
            raise ValueError(f"Failed to set {agent_name} to {status}.")
        return {"agent": agent_name, "status": new_status}
    except Exception as e:
        logging.error(f"Error toggling agent status: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 3. Run the Full Pipeline
@app.post("/run-pipeline")
async def run_pipeline(request: RunPipelineRequest):
    """
    Run the full pipeline, respecting agent activation states and parameters sent from the frontend.
    """
    try:
        logging.debug("Received request:", request)
        if request.flag_use_database_routing_agent:
            request.db_id = None
        result = agent_center.run_pipeline(
            question=request.question,
            flag_use_database_routing_agent=request.flag_use_database_routing_agent,
            db_id=request.db_id,
            flag_use_demonstration_selection_agent=request.flag_use_demonstration_selection_agent,
            num_demonstrations=request.num_demonstrations,
            prompt_template=request.prompt_template,
            model=request.model,
            flag_use_error_correction_agent=request.flag_use_error_correction_agent,
            flag_use_sql_execution_agent=request.flag_use_sql_execution_agent
        )
        result["status"] = "success"
        for key in result:
            if result[key] is None:
                ## replace with empty string
                result[key] = ''
        return result
    except Exception as e:
        logging.error(f"Error running pipeline:\n{e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# 4. SQL Execution (Manual)
@app.post("/execute-sql")
async def execute_sql(request: SQLExecutionRequest):
    """
    Execute a SQL query on a specific database.
    """
    try:
        logging.debug(f"Received request: {request}")
        logging.debug(f"SQL Execution result for query {request.sql_query} on database {request.db_id}")
        result = agent_center.execute_agent('SQL Execution Agent', request.sql_query, request.db_id)
        logging.debug(f"SQL Execution result:\n{result}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Fetch Schema for a Database
@app.post("/fetch-schema")
async def fetch_schema(request: FetchSchemaRequest):
    """
    Fetch the schema of a database using the SchemaFetchingAgent.
    """
    try:
        if not request.db_id:
            raise HTTPException(status_code=400, detail="Database ID (db_id) is required for schema fetching.")
        
        schema_text = agent_center.schema_fetching_agent.run(request.db_id)
        return {"status": "success", "schema": schema_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema: {str(e)}")

# 6. Select Demonstrations for a Question
@app.post("/select-demonstrations")
async def select_demonstrations(request: SelectDemonstrationsRequest):
    """
    Select demonstrations based on the user's question using the DemonstrationSelectionAgent.
    """
    try:
        demonstrations_text = agent_center.demonstration_selection_agent.run(
            request.question, demonstration_selector_option='jaccard', num_demonstrations=request.num_demonstrations
        )
        return {"status": "success", "demonstrations": demonstrations_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to select demonstrations: {str(e)}")

# 7. Construct SQL Prompt
@app.post("/construct-prompt")
async def construct_prompt(request: ConstructPromptRequest):
    """
    Construct a SQL prompt using the PromptConstructionAgent.
    """
    try:
        schema_text = agent_center.schema_fetching_agent.run(request.db_id)
        demonstrations_text = agent_center.demonstration_selection_agent.run(
            request.question, demonstration_selector_option='jaccard', num_demonstrations=request.num_demonstrations
        )
        prompt_text, prompt_result = agent_center.prompt_construction_agent.run(request.question, schema_text, demonstrations_text)
        return {"status": "success", "prompt_text": prompt_text, "result": prompt_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to construct prompt: {str(e)}")

# 8. Apply Error Correction to SQL Prompt
@app.post("/apply-error-correction")
async def apply_error_correction(request: ApplyErrorCorrectionRequest):
    """
    Apply error correction to an SQL query using the ErrorCorrectionAgent.
    """
    try:
        schema_text = agent_center.schema_fetching_agent.run(request.db_id)
        demonstrations_text = agent_center.demonstration_selection_agent.run(
            request.question, demonstration_selector_option='jaccard', num_demonstrations=request.num_demonstrations
        )
        prompt_text, corrected_result = agent_center.error_correction_agent.run(request.question, schema_text, demonstrations_text)
        return {"status": "success", "corrected_result": corrected_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply error correction: {str(e)}")


@app.post("/retrieve-gold-sql")
async def retrieve_gold_sql(request: GoldSQLRetrievalRequest):
    question = request.question
    try:
        most_similar_sql, most_similar_question = gold_sql_retrieval.get_most_similar_sql(question)
        return most_similar_sql
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve gold SQL: {str(e)}")
    

@app.post("/execute-prompt-construction-agent")
async def execute_prompt_construction_agent(request: ExecutePromptConstructionAgentRequest):
    try:
        prompt_text, prompt_res = agent_center.prompt_construction_agent.run(
            request.question,
            request.schema_text if request.schema_text else None,
            request.demonstration_text if request.demonstration_text else None, 
            template_option=request.template_option,
            model=request.model
        )
        return {"prompt_text": prompt_text, "prompt_result": prompt_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute Prompt Construction Agent: {str(e)}")
    
@app.post("/execute-error-correction-agent")
async def execute_error_correction_agent(request: ExecuteErrorCorrectionAgentRequest):
    try:
        prompt_text, prompt_result = agent_center.error_correction_agent.run(
            request.question,
            request.sql_query,
            schema_text=request.schema_text if request.schema_text else None,
            rules_groups=request.rules_groups if request.rules_groups else [1,3,4],
            model=request.model
        )
        return {"prompt_text": prompt_text, "prompt_result": prompt_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute Error Correction Agent: {str(e)}")


@app.post("/execute-error-correction-agent-with-generated-prompt")
async def execute_error_correction_agent_with_generated_prompt(request: ExecuteErrorCorrectionAgentWithGeneratedPromptRequest):
    try:
        prompt_text, prompt_result = agent_center.error_correction_agent.run_with_generated_prompt(
            request.prompt_text, 
        )
        return {"prompt_text": prompt_text, "prompt_result": prompt_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute Demonstration Selection Agent: {str(e)}")

@app.post("/execute-demonstration-selection-agent")
async def execute_demonstration_selection_agent(request: ExecuteDemonstrationSelectionAgentRequest):
    try:
        demonstrations_text = agent_center.demonstration_selection_agent.run(
            request.question, 
            demonstration_selector_option='jaccard',
            num_demonstrations=request.num_demonstrations
        )
        return {"demonstrations": demonstrations_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute Demonstration Selection Agent: {str(e)}")
    
@app.post("/execute-database-routing-agent")
async def execute_database_routing_agent(request: ExecuteDatabaseRoutingAgentRequest):
    try:
        db_id = agent_center.database_routing_agent.run(request.question)
        return {"db_id": db_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute Database Routing Agent: {str(e)}")