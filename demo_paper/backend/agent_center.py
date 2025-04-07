import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

import logging
logger = logging.getLogger(__name__)

from agents.data_loader_agent import DataLoaderAgent
from agents.database_routing_agent import DatabaseRoutingAgent
from agents.schema_fetching_agent import SchemaFetchingAgent
from agents.demonstration_selection_agent import DemonstrationSelectionAgent
from agents.prompt_construction_agent import PromptConstructionAgent
from agents.error_correction_agent import ErrorCorrectionAgent
from agents.sql_execution_agent import SqlExecutionAgent


class AgentCenter():
    def __init__(self):
        ## initialize all agents
        print("Initializing data loader agent...")
        self.data_loader_agent = DataLoaderAgent()
        ## set the base path as ../.. of current file path
        self.base_path = os.path.join(os.path.dirname(__file__), '..', '..')
        self.dataset_name = "spider"
        self.dataset_dir_path = os.path.join(self.base_path, 'datasets', self.dataset_name)
        self.dataset = self.data_loader_agent.run(self.dataset_name, self.dataset_dir_path)
        
        print("Initializing database routing agent...")
        self.database_routing_model_path = os.path.join(self.base_path, 'database_routing/saved_models/database_routing_spider_v1')
        self.database_routing_agent = DatabaseRoutingAgent(model_path=self.database_routing_model_path)
        
        print("Initializing schema fetching agent...")
        self.schema_file_path = os.path.join(self.base_path, 'datasets/spider/db_id2schema_text.json')
        self.schema_fetching_agent = SchemaFetchingAgent(cache_schema_path=self.schema_file_path)

        print("Initializing demonstration selection agent...")
        self.demonstration_selection_agent = DemonstrationSelectionAgent(dataset=self.dataset)
        
        print("Initializing prompt construction agent...")
        self.prompt_construction_agent = PromptConstructionAgent()

        print("Initializing error correction agent...")
        self.error_correction_agent = ErrorCorrectionAgent()

        print("Initializing sql execution agent...")
        # self.database_path = os.path.join(self.base_path, 'datasets/spider/database')
        self.database_path = os.path.join(self.base_path, 'datasets/spider/database_all_splits')
        self.sql_execution_agent = SqlExecutionAgent(database_path=self.database_path)

        print("Agent center initialized successfully.")

        # Set initial agent states
        self.agent_name2agent = {
            'Data Loader Agent': self.data_loader_agent,
            'Database Routing Agent': self.database_routing_agent,
            'Schema Fetching Agent': self.schema_fetching_agent,
            'Demonstration Selection Agent': self.demonstration_selection_agent,
            'Prompt Construction Agent': self.prompt_construction_agent,
            'Error Correction Agent': self.error_correction_agent,
            'SQL Execution Agent': self.sql_execution_agent,
        }
        self.agent_name2status = {agent_name: 'active' for agent_name in self.agent_name2agent.keys()}

    def toggle_agent_status(self, agent_name: str, agent_status: str):
        """
        Toggle the activation status of an agent.
        """
        if agent_name not in self.agent_name2status:
            raise ValueError(f"Agent {agent_name} not found.")
        
        # current_status = self.agent_name2status[agent_name]
        # self.agent_name2status[agent_name] = 'inactive' if current_status == 'active' else 'active'
        if agent_status not in ['active', 'inactive']:
            raise ValueError(f"Invalid agent status {agent_status}.")
        self.agent_name2status[agent_name] = agent_status
        logger.debug(f"Set {agent_name} to {agent_status}.")
        ## print the current status of all agents
        logger.debug(f"Current agent status: {self.agent_name2status}")

        return self.agent_name2status[agent_name]

    def get_agent_status(self, agent_name: str):
        """
        Get the current activation status of an agent.
        """
        return self.agent_name2status.get(agent_name, 'inactive')

    def execute_agent(self, agent_name: str, *args):
        """
        Execute a specific agent if it's active, considering dependencies.
        For agents that depend on other agents, behavior may vary.
        """
        if self.agent_name2status[agent_name] != 'active':
            raise ValueError(f"Agent {agent_name} is inactive.")

        if agent_name == 'Prompt Construction Agent' and self.get_agent_status('Schema Fetching Agent') == 'inactive':
            raise ValueError("Schema Fetching Agent must be active for Prompt Construction Agent to work.")

        if agent_name == 'Error Correction Agent' and self.get_agent_status('Prompt Construction Agent') == 'inactive':
            raise ValueError("Prompt Construction Agent must be active for Error Correction Agent to work.")

        # Execute the agent's run method
        agent = self.agent_name2agent[agent_name]
        return agent.run(*args)

    def run_pipeline(
        self, 
        question: str, 
        flag_use_database_routing_agent: bool = True, 
        db_id: str = None, 
        flag_use_demonstration_selection_agent: bool = True, 
        num_demonstrations: int = 5, 
        prompt_template: str = 'option_1', 
        model: str = 'gpt-4', 
        flag_use_error_correction_agent: bool = True,
        flag_use_sql_execution_agent: bool = True
    ):
        """
        Run the full pipeline, considering agent states and using parameters from the frontend.
        """
        print("Running pipeline with the following parameters:")
        print(f"Question: {question}")
        print(f"Use Database Routing Agent: {flag_use_database_routing_agent}")
        print(f"DB ID: {db_id}")
        print(f"Use Demonstration Selection Agent: {flag_use_demonstration_selection_agent}")
        print(f"Number of Demonstrations: {num_demonstrations}")
        print(f"Prompt Template: {prompt_template}")
        print(f"Model: {model}")
        print(f"Use Error Correction Agent: {flag_use_error_correction_agent}")

        schema_text = None
        demonstrations_text = None
        generated_sql_for_exec = None

        # Step 1: If the Database Routing Agent is active, use it to get the db_id
        if flag_use_database_routing_agent and self.get_agent_status('Database Routing Agent') == 'active':
            db_id = self.database_routing_agent.run(question)

        # Step 2: Fetch the schema if the Schema Fetching Agent is active
        if self.get_agent_status('Schema Fetching Agent') == 'active':
            schema_text = self.schema_fetching_agent.run(db_id)

        # Step 3: Get demonstrations if the Demonstration Selection Agent is active
        if flag_use_demonstration_selection_agent and self.get_agent_status('Demonstration Selection Agent') == 'active':
            demonstrations_text = self.demonstration_selection_agent.run(question, demonstration_selector_option='jaccard', num_demonstrations=num_demonstrations)

        # Step 4: Use the Prompt Construction Agent to create the SQL query
        if self.get_agent_status('Prompt Construction Agent') == 'active':
            prompt_text, prompt_result = self.prompt_construction_agent.run(question, schema_text, demonstrations_text, prompt_template, model)
            generated_sql_for_exec = prompt_result
        else:
            raise ValueError("Prompt Construction Agent must be active for SQL generation.")

        # Step 5: If error correction is enabled and the Error Correction Agent is active, use it
        if flag_use_error_correction_agent and self.get_agent_status('Error Correction Agent') == 'active':
            correction_prompt_text, corrected_result = self.error_correction_agent.run(question, schema_text, demonstrations_text)
            generated_sql_for_exec = corrected_result
        else:
            correction_prompt_text = None
            corrected_result = None

        # Step 6: Execute the generated SQL using the SQL Execution Agent
        if flag_use_sql_execution_agent and self.get_agent_status('SQL Execution Agent') == 'active':
            sql_result = self.sql_execution_agent.run(generated_sql_for_exec, db_id)
        else:
            sql_result = None
        res = {
            "question": question,
            "db_id": db_id,
            "schema_text": schema_text,
            "demonstration_text": demonstrations_text,
            "prompt_construction_agent_prompt": prompt_text,
            "prompt_construction_agent_query": prompt_result,
            "error_correction_agent_prompt": correction_prompt_text,
            "error_correction_agent_query": corrected_result,
            "generated_sql_for_exec": generated_sql_for_exec,
            "generated_sql_exec_res": sql_result
        }
        logger.debug(f"Pipeline run successfully. Results:")
        logger.debug(f"Question: {question}")
        logger.debug(f"DB ID: {db_id}")
        logger.debug(f"Schema text: \n{schema_text}")
        logger.debug(f"Demonstrations text: \n{demonstrations_text}")
        logger.debug(f"Prompt text: \n{prompt_text}")
        logger.debug(f"Prompt result: {prompt_result}")
        logger.debug(f"Error correction prompt: \n{correction_prompt_text}")
        logger.debug(f"Corrected result: {corrected_result}")
        logger.debug(f"SQL query for execution: {res['generated_sql_for_exec']}")
        logger.debug(f"SQL execution result: {sql_result}")
        return res