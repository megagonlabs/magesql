import React, { useState, useCallback, useEffect, useContext } from 'react';
import { Tabs, Tab, Button, Intent, Divider, Dialog, FormGroup, InputGroup } from "@blueprintjs/core";
import Header from './components/Header';
import ConnectionForm from './components/ConnectionForm';
import SidebarNavigation from './components/SidebarNavigation';
import MainTab from './components/MainTab';
import AgentTab from './components/AgentTab';
import ExperimentalResultsTab from './components/ExperimentalResultsTab';
import { AgentProvider, useAgent } from './context/AgentContext';
import '@blueprintjs/core/lib/css/blueprint.css';
import './App.css';
import logo from './assets/logo_v3.png';
import { retrieveGoldSQL } from './api/agentApi'; 

function App() {
  const [selectedTabId, setSelectedTabId] = useState('main');
  const [compareTrigger, setCompareTrigger] = useState(false);

  const {
    agents, selectedAgent, setSelectedAgent, resetAgentsStatus, 
    pipelineStatus, executePipeline, executeSelectedAgent, 
    handleSaveResults, agentExecutionStatus, question, setQuestion,
    database, setDatabase,
    goldSQL, setGoldSQL,
    SQLForExecution, setSQLForExecution,
    compareAndHighlightResults, loadingComparison,
    loadingFinalSQLExecution, setLoadingFinalSQLExecution,
    loadingGoldSQLExecution, setLoadingGoldSQLExecution,
    executeFinalSQL, executeGoldSQL,
    correctionPrompt, executeCustomErrorCorrection,
    executeCustomErrorCorrectionAgent,
  } = useAgent();

  // // Function to update agent inputs (called from AgentTab)
  // const updateAgentInputs = useCallback((inputs) => {
  //   setAgentInputs(inputs);
  // }, []);

  // Select agent and switch to the Agent tab, if agent is active
  const selectAgentTab = (agentName) => {
    const agent = agents.find(agent => agent.name === agentName);
    if (agent && agent.isActive) {
        setSelectedAgent(agent);
        if (agentName === "SQL Execution Agent") {
          setSelectedTabId('results'); // Directly jump to ExperimentalResultsTab for "SQL Execution Agent"
        } else {
            setSelectedTabId('agent'); // For other agents, continue jumping to the AgentTab
        }
    }
  };

  const [loadingGoldSQL, setLoadingGoldSQL] = useState(false); // State for the "Retrieve Gold SQL" button

  // Function to handle retrieving Gold SQL from the backend
  const handleRetrieveGoldSQL = useCallback(async () => {
    setLoadingGoldSQL(true);
    try {
      const data = await retrieveGoldSQL(question); // Retrieve the gold SQL from the backend
      console.log("Gold SQL retrieved:", data);
      setGoldSQL(data);
    } catch (error) {
      console.error("Failed to retrieve Gold SQL", error);
    } finally {
      setLoadingGoldSQL(false);
    }
  }, [question, setGoldSQL]); // Re-run the effect when the question changes


  // const [compareResultStatus, setCompareResultStatus] = useState("idle"); // "idle", "running", "completed"
  // // Placeholder function to handle comparing results
  // const handleCompareResults = useCallback(async () => {
  //   setCompareResultStatus("running");
  //   console.log("Comparing results...");
  //   // Simulate a long-running operation
  //   setTimeout(() => {
  //     setCompareTrigger(prev => !prev);
  //     setCompareResultStatus("completed");
  //     setTimeout(() => setCompareResultStatus("idle"), 500);
  //   }, 500);
  // }, []);
  const handleCompareResults = useCallback(async () => {
    try {
      await compareAndHighlightResults();
    } catch (error) {
      console.error("Error comparing results:", error);
    }
  }, [compareAndHighlightResults]);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [tempQuestion, setTempQuestion] = useState(question || "");
  const [tempDatabaseId, setTempDatabaseId] = useState(database || "");
  const isDatabaseRoutingActive = agents.some(agent => agent.name === 'Database Routing Agent' && agent.isActive);


  const handleOpenDialog = useCallback(() => {
    console.log("Opening question input dialog");
    setTempQuestion(question || "");
    setTempDatabaseId(database || "");
    setIsDialogOpen(true);
  }, []);

  const handleCloseDialog = useCallback(() => {
    console.log("Cancelled question input");
    setIsDialogOpen(false);
  }, []);

  const handleConfirmDialog = useCallback(() => {
    console.log("Confirmed question:", tempQuestion);
    setQuestion(tempQuestion);
    console.log("The question in context before pipeline exec is:", question);
    if (!isDatabaseRoutingActive && tempDatabaseId.trim() === "") {
      console.error("Database ID is required when Database Routing Agent is not active.");
      return;
    }
    if (!isDatabaseRoutingActive) {
      setDatabase(tempDatabaseId);
    }
    console.log("The database in context before pipeline exec is:", database);
    
    console.log("Executing pipeline with question:", tempQuestion);
    console.log("Executing pipeline with Database ID:", tempDatabaseId);

    executePipeline(
      tempQuestion,
      isDatabaseRoutingActive ? null : tempDatabaseId,  // If the agent is active, no need to pass databaseId
    );
    
    console.log("The question in context after pipeline exec is:", question);
    setIsDialogOpen(false);
  }, [tempQuestion, tempDatabaseId, setQuestion, setDatabase, executePipeline, isDatabaseRoutingActive]);

  
const handleExecuteCustomErrorCorrection = () => {
  if (correctionPrompt.trim() === "") {
    console.warn("Correction Prompt is empty. Please enter the prompt text.");
    return;
  }
  executeCustomErrorCorrectionAgent(correctionPrompt);
};


  // Function to render the buttons based on the selected tab
  const renderButtons = useCallback(() => {
    switch (selectedTabId) {
      case 'main':
        return (
          <>
            <Button
              icon="play"
              text={"Execute Pipeline"}
              // onClick={executePipeline}
              onClick={handleOpenDialog}
              intent={Intent.PRIMARY}
              disabled={pipelineStatus === "running"}
            />
            <Dialog
              isOpen={isDialogOpen}
              onClose={handleCloseDialog}
              title="Please Enter a Question for Pipeline Execution"
              canEscapeKeyClose={true}
              canOutsideClickClose={true}
              className="custom-dialog"
            >
              <div className="bp4-dialog-body">
                <div style={{ marginTop: '10px' }}> 
                <FormGroup label="Enter your question">
                  <InputGroup 
                    id="text-input" 
                    placeholder="Enter your question here" 
                    value={tempQuestion} 
                    onChange={e => setTempQuestion(e.target.value)}
                  />
                </FormGroup>

                {/* Conditionally render Database ID input if Database Routing Agent is inactive */}
                {!isDatabaseRoutingActive && (
                  <FormGroup label="Database ID">
                    <InputGroup 
                      id="database-input" 
                      placeholder="Enter database ID here" 
                      value={tempDatabaseId} 
                      onChange={e => setTempDatabaseId(e.target.value)} 
                    />
                  </FormGroup>
                )}
                </div>
              </div>
              <div className="bp4-dialog-footer" style={{ paddingLeft: '10px', paddingRight: '0px', paddingBottom: '10px' }}>
                <div className="bp4-dialog-footer-actions">
                  <Button intent="primary" text="OK" onClick={handleConfirmDialog} style={{marginRight: '10px'}}/>
                  <Button text="Cancel" onClick={handleCloseDialog} />
                </div>
              </div>
            </Dialog>
            {/* <Button icon="play" text="Execute Pipeline" onClick={executePipeline} intent={Intent.PRIMARY} /> */}
            <Button icon="reset" text="Reset" onClick={resetAgentsStatus} intent={Intent.WARNING} />
          </>
        );
      case 'agent':
        return (
          <>
            <Button 
              icon="play"
              text="Execute Agent"
              onClick={executeSelectedAgent}
              intent={Intent.PRIMARY}
              disabled={agentExecutionStatus === "running"}
            />
            {selectedAgent && selectedAgent.name === "Error Correction Agent" && (
              <Button 
                icon="play"
                text="Execute Custom Correction Prompt"
                onClick={handleExecuteCustomErrorCorrection}
                intent={Intent.PRIMARY}
                disabled={agentExecutionStatus === "running"}
              />
          )}
        </>
        );
      case 'results': // Handle buttons for the "Experimental Results" tab
        return (
          <>
            <Button 
              icon="database"
              text="Retrieve Gold SQL" 
              onClick={handleRetrieveGoldSQL} 
              intent={Intent.PRIMARY} 
              loading={loadingGoldSQL} 
            />
            <Button
              icon="play"
              text="Execute Generated SQL"
              onClick={executeFinalSQL}
              intent={Intent.PRIMARY}
              loading={loadingFinalSQLExecution}
            />
            <Button
              icon="play"
              text="Execute Gold SQL"
              onClick={executeGoldSQL}
              intent={Intent.PRIMARY}
              loading={loadingGoldSQLExecution}
            />
            <Button 
            icon="comparison" 
            text="Compare Results" 
            onClick={handleCompareResults} 
            intent={Intent.PRIMARY} 
            disabled={loadingComparison}
            />
            
            <Button 
              icon="floppy-disk" 
              text="Save Results" 
              onClick={handleSaveResults} 
              intent={Intent.SUCCESS} 
            />
          </>
        );
      default:
        return null;
    }
  }, [selectedTabId, executePipeline, resetAgentsStatus, executeSelectedAgent, handleCompareResults, handleSaveResults, pipelineStatus, handleOpenDialog, isDialogOpen, handleCloseDialog, handleConfirmDialog]);

  return (
    <div className="App">
      <Header logo={logo} title="Demonstration of a Multi-agent Framework for Text to SQL Applications with Large Language Models" version="1.2" />
      <div className="app-body">
        <div className="left-panel">
          <ConnectionForm onConnect={() => { }} />
          <Divider className="left-panel-divider" orientation="horizontal" />
          <SidebarNavigation selectAgentTab={selectAgentTab} />
        </div>
        <div className="main-and-button-area">
          <div className="tabs-container">
            <Tabs id="TabsExample" selectedTabId={selectedTabId} onChange={setSelectedTabId}>
              <Tab id="main" title="Main" panel={
                <div className="tab-content">
                  <MainTab selectAgentTab={selectAgentTab}/>
                </div>
              } />
              <Tab id="agent" title="Agent" panel={
                <div className="tab-content">
                  <AgentTab />
                </div>
              } />
              <Tab id="results" title="Experimental Results" panel={
                <div className="tab-content">
                  <ExperimentalResultsTab compareTrigger={compareTrigger} />
                </div>
              } />
            </Tabs>
          </div>
          <div className="button-area">
            {renderButtons()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
