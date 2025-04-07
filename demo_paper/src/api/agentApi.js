const API_BASE_URL = 'http://localhost:8000';

// Helper function to handle responses and errors
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An error occurred');
  }
  return response.json();
};

// Function to toggle agent status
export const toggleAgentStatus = async (agentName, agentStatus) => {
  const response = await fetch(`${API_BASE_URL}/agents/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_name: agentName,
      status: agentStatus
    }),
  });
  return handleResponse(response);
};

// Function to run the full pipeline
export const runPipeline = async ({
  question,
  flagUseDatabaseRoutingAgent,
  dbId,
  flagUseDemonstrationSelectionAgent,
  numDemonstrations,
  promptTemplate,
  model,
  flagUseErrorCorrectionAgent,
  flagUseSQLExecutionAgent
}) => {
  const response = await fetch(`${API_BASE_URL}/run-pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      flag_use_database_routing_agent: flagUseDatabaseRoutingAgent,
      db_id: dbId,
      flag_use_demonstration_selection_agent: flagUseDemonstrationSelectionAgent,
      num_demonstrations: numDemonstrations,
      prompt_template: promptTemplate,
      model: model,
      flag_use_error_correction_agent: flagUseErrorCorrectionAgent,
      flag_use_sql_execution_agent: flagUseSQLExecutionAgent
    }),
  });
  return handleResponse(response);
};

// Function to manually execute SQL
export const executeSQL = async (sqlQuery, dbId) => {
  console.log("Executing SQL:", sqlQuery);
  const response = await fetch(`${API_BASE_URL}/execute-sql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sql_query: sqlQuery,
      db_id: dbId
    }),
  });
  return handleResponse(response);
};

// Function to fetch schema for a specific database
export const fetchSchema = async (dbId) => {
  const response = await fetch(`${API_BASE_URL}/fetch-schema`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      db_id: dbId
    }),
  });
  return handleResponse(response);
};

// Function to select demonstrations
export const selectDemonstrations = async (question, numDemonstrations = 5) => {
  const response = await fetch(`${API_BASE_URL}/select-demonstrations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      num_demonstrations: numDemonstrations
    }),
  });
  return handleResponse(response);
};

// Function to construct a SQL prompt
export const constructPrompt = async ({
  question,
  dbId,
  numDemonstrations = 5,
  promptTemplate = 'template1',
  model = 'gpt-4'
}) => {
  const response = await fetch(`${API_BASE_URL}/construct-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      db_id: dbId,
      num_demonstrations: numDemonstrations,
      prompt_template: promptTemplate,
      model: model
    }),
  });
  return handleResponse(response);
};

// Function to apply error correction to an SQL query
export const applyErrorCorrection = async ({
  question,
  dbId,
  numDemonstrations = 5,
}) => {
  const response = await fetch(`${API_BASE_URL}/apply-error-correction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      db_id: dbId,
      num_demonstrations: numDemonstrations
    }),
  });
  return handleResponse(response);
};


// Function to retrieve the Gold SQL
export const retrieveGoldSQL = async (question) => {
  const response = await fetch(`${API_BASE_URL}/retrieve-gold-sql`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  return handleResponse(response);
};


export const executePromptConstructionAgent = async (question, schema_text='', demonstration_text='', prompt_template = 'option_1', model = 'gpt-4') => {
  const response = await fetch(`${API_BASE_URL}/execute-prompt-construction-agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      schema_text: schema_text,
      demonstration_text: demonstration_text,
      template_option: prompt_template,
      model: model
    }),
  });
  return handleResponse(response);
}

export const executeErrorCorrectionAgent = async (question, sql_query, schema_text='', rules_groups=[1,2,3], model = 'gpt-4') => {
  // change 2 in rules_groups to 4 according to updates in the backend
  if (rules_groups.includes(2)) {
    rules_groups = rules_groups.filter((g) => g !== 2);
    rules_groups.push(4);
  }
  const response = await fetch(`${API_BASE_URL}/execute-error-correction-agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      sql_query: sql_query,
      schema_text: schema_text,
      rules_groups: rules_groups,
      model: model
    }),
  });
  return handleResponse(response);
}

export const executeErrorCorrectionAgentWithGeneratedPrompt = async (prompt_text, model='gpt-4') => {
  const response = await fetch(`${API_BASE_URL}/execute-error-correction-agent-with-generated-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt_text: prompt_text,
      model: model
    }),
  });
  return handleResponse(response);
}

export const executeDemonstrationSelectionAgent = async (question, num_demonstrations=5) => {
  const response = await fetch(`${API_BASE_URL}/execute-demonstration-selection-agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      num_demonstrations: num_demonstrations
    }),
  });
  return handleResponse(response);
}

export const executeDatabaseRoutingAgent = async (question) => {
  const response = await fetch(`${API_BASE_URL}/execute-database-routing-agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  return handleResponse(response);
}