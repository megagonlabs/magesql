import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { toggleAgentStatus, runPipeline, retrieveGoldSQL, executeSQL ,executePromptConstructionAgent, executeErrorCorrectionAgentWithGeneratedPrompt} from '../api/agentApi';  // Import the API functions
import { Toaster, Position, Intent } from "@blueprintjs/core";

const AgentContext = createContext();

export const useAgent = () => useContext(AgentContext);

const AppToaster = Toaster.create({
    position: Position.BOTTOM,
  });

const initialAgents = [
  { name: "Data Loader Agent", icon: "database", isActive: true },
  { name: "Database Routing Agent", icon: "search-around", isActive: false },
  { name: "Demonstration Selection Agent", icon: "select", isActive: false },
  { name: "Prompt Construction Agent", icon: "build", isActive: true },
  { name: "Error Correction Agent", icon: "issue-closed", isActive: false },
  { name: "SQL Execution Agent", icon: "play", isActive: false },
];

export const AgentProvider = ({ children }) => {
  const [selectedAgent, setSelectedAgent] = useState(null); // State for selected agent
  const [agents, setAgents] = useState(initialAgents); // State for all agents
  const [question, setQuestion] = useState("");
  const [database, setDatabase] = useState("");
  const [databaseSchema, setDatabaseSchema] = useState("");

  const [demonstrations, setDemonstrations] = useState("");
  const [numDemonstrations, setNumDemonstrations] = useState(5); // Default to 5
  const [promptConstructionTemplate, setPromptConstructionTemplate] = useState("option_1");
  const [promptConstructionModel, setPromptConstructionModel] = useState("gpt-4");
  const [generatedPrompt, setGeneratedPrompt] = useState("");
  const [generatedSQL, setGeneratedSQL] = useState("");

  const [correctionPrompt, setCorrectionPrompt] = useState("");
  const [correctionModel, setCorrectionModel] = useState("gpt-4");
  const [correctedSQL, setCorrectedSQL] = useState("");

  const [SQLForExecution, setSQLForExecution] = useState("");
  const [executionResults, setExecutionResults] = useState([]);
  const [goldSQL, setGoldSQL] = useState(""); 
  const [goldExecutionResults, setGoldExecutionResults] = useState([]);
  const [isResultsSame, setIsResultsSame] = useState(true); 
  const [showComparedResults, setShowComparedResults] = useState(false);
  const [modifiedGeneratedResults, setModifiedGeneratedResults] = useState([]);
  const [comparisonText, setComparisonText] = useState('');
  const [loadingFinalSQLExecution, setLoadingFinalSQLExecution] = useState(false);
  const [loadingGoldSQLExecution, setLoadingGoldSQLExecution] = useState(false);
  
  const [pipelineStatus, setPipelineStatus] = useState("idle"); // "idle", "running", "completed"
  const [agentExecutionStatus, setAgentExecutionStatus] = useState({});

  // Triggers for agent execution
  const [databaseRoutingAgentTrigger, setDatabaseRoutingAgentTrigger] = useState(false);
  const [demonstrationAgentTrigger, setDemonstrationAgentTrigger] = useState(false);
  const [promptAgentTrigger, setPromptAgentTrigger] = useState(false);
  const [correctionAgentTrigger, setCorrectionAgentTrigger] = useState(false);

  // Function to toggle agent activation and send the updated status to the backend
  const toggleAgentActive = async (agentName) => {
    const updatedAgents = agents.map(agent =>
      agent.name === agentName ? { ...agent, isActive: !agent.isActive } : agent
    );
    setAgents(updatedAgents);  // Update frontend state

    // Find the updated status (active/inactive) for the toggled agent
    const agentStatus = updatedAgents.find(agent => agent.name === agentName)?.isActive ? 'active' : 'inactive';

    // Send the updated status to the backend
    try {
      await toggleAgentStatus(agentName, agentStatus);
      console.log(`Agent ${agentName} updated to ${agentStatus} on backend.`);
    } catch (error) {
      console.error(`Failed to update agent ${agentName} on backend:`, error);
    }
  };

  // Reset agent statuses to default
  const resetAgentsStatus = () => {
    console.log("Resetting agent statuses...");
  
    // Reset all agent states
    setSelectedAgent(null);
    setAgents(initialAgents);
  
    // Reset question and database
    setQuestion("");
    setDatabase("");
    setDatabaseSchema("");
    setDemonstrations("");
    setNumDemonstrations(5);
    setPromptConstructionTemplate("option_1");
    setPromptConstructionModel("gpt-4");
    setGeneratedPrompt("");
    setGeneratedSQL("");
    setCorrectionPrompt("");
    setCorrectionModel("gpt-4");
    setCorrectedSQL("");
    setSQLForExecution("");
    setExecutionResults([]);
    setGoldSQL("");
    setGoldExecutionResults([]);
    setIsResultsSame(true);
    setShowComparedResults(false);
    setModifiedGeneratedResults([]);
    setComparisonText("");
    setLoadingFinalSQLExecution(false);
    setLoadingGoldSQLExecution(false);
  
    setPipelineStatus("idle");
    setAgentExecutionStatus({});
    
    // Reset any agent triggers if necessary
    setDemonstrationAgentTrigger(false);
    setPromptAgentTrigger(false);
    setCorrectionAgentTrigger(false);
  };

  const errorCorrectionAgentIsActive = agents.find(agent => agent.name === "Error Correction Agent")?.isActive || false;

  // Monitor changes to `generatedSQL` and `correctedSQL` and update `SQLForExecution` accordingly
  useEffect(() => {
    if (errorCorrectionAgentIsActive && correctedSQL) {
      setSQLForExecution(correctedSQL); // Use corrected SQL if Error Correction Agent is active
    } else if (generatedSQL) {
      setSQLForExecution(generatedSQL); // Otherwise, use generated SQL
    }
  }, [generatedSQL, correctedSQL, errorCorrectionAgentIsActive]); 

  const executePipeline = async (updatedQuestion, database_id_in_dialog) => {
    setPipelineStatus("running");
    setQuestion("");
    setDatabase("");
    setDatabaseSchema("");
    setDemonstrations("");
    setNumDemonstrations(5);
    setPromptConstructionTemplate("option_1");
    setPromptConstructionModel("gpt-4");
    setGeneratedPrompt("");
    setGeneratedSQL("");
    setCorrectionPrompt("");
    setCorrectionModel("gpt-4");
    setCorrectedSQL("");
    setSQLForExecution("");
    setExecutionResults([]);
    setGoldSQL("");
    setGoldExecutionResults([]);
    setIsResultsSame(true);
    setShowComparedResults(false);
    setModifiedGeneratedResults([]);
    setComparisonText("");
    setLoadingFinalSQLExecution(false);
    setLoadingGoldSQLExecution(false);
    setAgentExecutionStatus({});
    // Gather all the necessary data for the pipeline
    const activeAgents = agents.filter(agent => agent.isActive);
    const flagUseDatabaseRoutingAgent = activeAgents.some(agent => agent.name === 'Database Routing Agent');
    const flagUseDemonstrationSelectionAgent = activeAgents.some(agent => agent.name === 'Demonstration Selection Agent');
    const flagUseErrorCorrectionAgent = activeAgents.some(agent => agent.name === 'Error Correction Agent');
    const flagUseSQLExecutionAgent = activeAgents.some(agent => agent.name === 'SQL Execution Agent');
    // const numDemonstrations = 5;

    try {
      console.log("Executing pipeline with question:", updatedQuestion);
      const response = await runPipeline({
        // question: question,
        question: updatedQuestion, // React seems update state asynchronously
        flagUseDatabaseRoutingAgent,
        dbId: database_id_in_dialog,
        flagUseDemonstrationSelectionAgent,
        numDemonstrations,
        promptTemplate: promptConstructionTemplate,
        model: promptConstructionModel,
        flagUseErrorCorrectionAgent,
        flagUseSQLExecutionAgent,
      });

      // Update the context values with the response from the pipeline
      setQuestion(response.question); // Set the question (if needed)
    //   if (flagUseDatabaseRoutingAgent) {
    //     setDatabase(response.db_id); // Set the database id
    //   }
      setDatabase(response.db_id); // Set the database id regardless of agent activation
      setDatabaseSchema(response.schema_text);  // Update the database schema from the response
      if (flagUseDemonstrationSelectionAgent) {
        setDemonstrations(response.demonstration_text);  // Set demonstrations
      }
      setGeneratedPrompt(response.prompt_construction_agent_prompt); // Set the generated prompt
      setGeneratedSQL(response.prompt_construction_agent_query);  // Set the generated SQL
      if (flagUseErrorCorrectionAgent) {
        setCorrectionPrompt(response.error_correction_agent_prompt);  // Set the corrected prompt
        setCorrectedSQL(response.error_correction_agent_query);  // Set the corrected SQL
        setSQLForExecution(response.error_correction_agent_query);  // Set the corrected SQL for execution
      }
      else {
        setSQLForExecution(response.prompt_construction_agent_query);  // Set the generated SQL for execution
      }
      if (flagUseSQLExecutionAgent) {
        console.log("Sql execution result:", response.generated_sql_exec_res);
        // generated_sql_exec_res is dictionary with keys: query_exec_flag, query_exec_result
        // if query_exec_flag is not "result", that means query_exec_result is error message
        if (response.generated_sql_exec_res.query_exec_flag === "error") {
          console.error("Error executing SQL:", response.generated_sql_exec_res.query_exec_result);
          setPipelineStatus("failed");
          AppToaster.show({
            message: `Error executing SQL: ${response.generated_sql_exec_res.query_exec_result}`,
            intent: Intent.DANGER,
            timeout: 3000,
          });
          return;
        }
        setExecutionResults(response.generated_sql_exec_res.query_exec_result);
      }
      
        // Set execution results
      
    //   setGoldSQL(response.gold_sql);  // Set gold SQL from backend

      console.log("Pipeline execution result:", response);
      setPipelineStatus("completed");
        // Show success notification
        AppToaster.show({
            message: "Pipeline executed successfully.",
            intent: Intent.SUCCESS,
            timeout: 3000,
        });

    } catch (error) {
        console.error("Error executing pipeline:", error);
        setPipelineStatus("failed");

        // Show error notification
        const errorMessage = error.response?.data?.detail || error.message || "Failed to execute pipeline.";
        AppToaster.show({
            message: `Pipeline error: ${errorMessage}`,
            intent: Intent.DANGER,
            timeout: 3000,
        });
    }
};

  // Function to trigger selected agent execution
  const executeSelectedAgent = () => {
    if (selectedAgent.name === "Prompt Construction Agent") {
      setPromptAgentTrigger(prev => !prev); // Toggle the prompt agent trigger
    } else if (selectedAgent.name === "Error Correction Agent") {
      setCorrectionAgentTrigger(prev => !prev); // Toggle the error correction agent trigger
    } else if (selectedAgent.name === "Demonstration Selection Agent") {
      setDemonstrationAgentTrigger(prev => !prev); // Trigger execution for demonstration agent
    }
  };

  const executeCustomErrorCorrectionAgent = async (correctionPrompt) => {
    try {
      setAgentExecutionStatus("running");
      const response = await executeErrorCorrectionAgentWithGeneratedPrompt(correctionPrompt);
      setCorrectedSQL(response.prompt_result); // Update the corrected SQL
      setAgentExecutionStatus("completed");
    } catch (error) {
      console.error("Error executing custom Error Correction Agent:", error);
      setAgentExecutionStatus("failed");
    }
  };

//   // Execute SQL (Placeholder for actual functionality)
//   const executeSQL = () => {
//     const newResults = [{ id: 1, result: 'Example SQL execution result' }];
//     setExecutionResults(newResults);
//   };

  // Placeholder function to handle saving results
  const handleSaveResults = () => {
    console.log("Saving execution results...");
  };

//   // Retrieve Gold SQL
//   const retrieveGoldSQLFromBackend = async () => {
//     try {
//       const response = await retrieveGoldSQL(question); 
//       setGoldSQL(response); 
//     } catch (error) {
//       console.error("Failed to retrieve Gold SQL", error);
//     }
//     };
  const executeFinalSQL = async () => {
    setLoadingFinalSQLExecution(true);
    setShowComparedResults(false);
    setExecutionResults(null); // Clear the previous state
    try {
      const result = await executeSQL(SQLForExecution, database);
      if (result.status === "error") {
        setExecutionResults(result.error_message); // Store error message as string
      } else {
        setExecutionResults(result.query_exec_result); // Store results as an array
      }
    } catch (error) {
      console.error("Error executing generated SQL:", error);
      setExecutionResults("Failed to execute generated SQL.");
    } finally {
      setLoadingFinalSQLExecution(false);
    }
  };

  const executeGoldSQL = async () => {
    setLoadingGoldSQLExecution(true);
    setShowComparedResults(false);
    setGoldExecutionResults(null); // Clear the previous state
    try {
        const result = await executeSQL(goldSQL, database);
        if (result.status === "error") {
            setGoldExecutionResults(result.error_message); // Store error message as string
        } else {
            setGoldExecutionResults(result.query_exec_result); // Store results as an array
        }
    } catch (error) {
        console.error("Error executing Gold SQL:", error);
        setGoldExecutionResults("Failed to execute Gold SQL.");
    } finally {
        setLoadingGoldSQLExecution(false);
    }
  };

  const compareAndHighlightResults = useCallback(async () => {
    try {
      console.log("Gold SQL:", goldSQL);
      const goldExecutionResponse = await executeSQL(goldSQL, database);
      if (goldExecutionResponse.status === "error") { 
        console.log("Error executing Gold SQL:", goldExecutionResponse.error_message);
        setGoldExecutionResults(goldExecutionResponse.error_message);
        return
      }
      setGoldExecutionResults(goldExecutionResponse.query_exec_result);
      const goldResults = goldExecutionResponse.query_exec_result;
  
      let resultsMatch = true;
      const updatedGeneratedResults = executionResults.map(genResult => {
        const isInGold = goldResults.some(goldRes => JSON.stringify(goldRes) === JSON.stringify(genResult));
        return { ...genResult, _style: isInGold ? 'regular' : 'false_positive' };
      });
  
      const addedRows = goldResults.filter(goldRes => 
        !executionResults.some(genResult => JSON.stringify(genResult) === JSON.stringify(goldRes))
      ).map(row => ({ ...row, _style: 'true_negative' }));
  
      const combinedResults = [...updatedGeneratedResults, ...addedRows];
      resultsMatch = addedRows.length === 0;
  
      setModifiedGeneratedResults(combinedResults);
      setShowComparedResults(true);
      setIsResultsSame(resultsMatch);
      setComparisonText(resultsMatch ? "The execution results are the same." : "The execution results are different.");
    } catch (error) {
      console.error("Error comparing results:", error);
    }
    }, [database, goldSQL, executionResults]);

  const value = {
    selectedAgent, setSelectedAgent,
    agents, setAgents,
    question, setQuestion,
    database, setDatabase,
    databaseSchema, setDatabaseSchema,
    demonstrations, setDemonstrations,
    numDemonstrations, setNumDemonstrations,
    promptConstructionTemplate, setPromptConstructionTemplate,
    promptConstructionModel, setPromptConstructionModel,
    generatedPrompt, setGeneratedPrompt,
    generatedSQL, setGeneratedSQL,
    correctionModel, setCorrectionModel,
    correctionPrompt, setCorrectionPrompt,
    correctedSQL, setCorrectedSQL,
    SQLForExecution, setSQLForExecution,
    executionResults, setExecutionResults,
    goldSQL, setGoldSQL,
    goldExecutionResults, setGoldExecutionResults,
    isResultsSame, setIsResultsSame,
    showComparedResults, setShowComparedResults,
    modifiedGeneratedResults, setModifiedGeneratedResults,
    comparisonText, setComparisonText,
    pipelineStatus, setPipelineStatus,
    agentExecutionStatus, setAgentExecutionStatus,
    toggleAgentActive, resetAgentsStatus,
    handleSaveResults, executeSelectedAgent, executeSQL, 
    executePipeline, 
    // retrieveGoldSQLFromBackend, 
    compareAndHighlightResults,
    databaseRoutingAgentTrigger, setDatabaseRoutingAgentTrigger,
    demonstrationAgentTrigger, setDemonstrationAgentTrigger,
    promptAgentTrigger, setPromptAgentTrigger,
    correctionAgentTrigger, setCorrectionAgentTrigger,
    loadingFinalSQLExecution, setLoadingFinalSQLExecution,
    loadingGoldSQLExecution, setLoadingGoldSQLExecution,
    executeFinalSQL, executeGoldSQL,
    executeCustomErrorCorrectionAgent,
  };

  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
};
