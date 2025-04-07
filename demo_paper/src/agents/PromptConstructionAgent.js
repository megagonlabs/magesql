import React, { useState, useEffect } from 'react';
import { Button, Card, Elevation, FormGroup, InputGroup, Radio, RadioGroup, TextArea, Divider, H3 } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import { executePromptConstructionAgent } from '../api/agentApi';

// Mock function to simulate fetching database schema
const fetchDatabaseSchema = async (databaseName) => {
  return `Schema for ${databaseName}`;
};

const getIconPath = (iconName) => {
  return `${process.env.PUBLIC_URL}/icons/${iconName}.svg`;
};

const AgentTab = () => {
  const {
    question, setQuestion,
    database, setDatabase,
    databaseSchema, setDatabaseSchema,
    demonstrations, setDemonstrations,
    generatedSQL, setGeneratedSQL,
    generatedPrompt, setGeneratedPrompt,
    selectedAgent,
    agentExecutionStatus, setAgentExecutionStatus,
    promptAgentTrigger,
    promptConstructionTemplate, setPromptConstructionTemplate,
    promptConstructionModel, setPromptConstructionModel,
  } = useAgent();

  const [showImportFields, setShowImportFields] = useState(false);
  
  // Safe access to selectedAgent properties
  const iconSrc = selectedAgent ? getIconPath(selectedAgent.icon) : '';

  // Handle database selection (simulate fetching schema)
  const handleDatabaseSelect = async (e) => {
    const dbName = e.target.value;
    setDatabase(dbName);
    // const schema = await fetchDatabaseSchema(dbName);
    // setGeneratedPrompt();
  };


  const toggleImportFields = () => {
    //sleep for 0.3 seconds
    // setTimeout(() => {
    //   setShowImportFields(!showImportFields);
    //   setGeneratedPrompt('<Placeholder>');
    // },700);
    setShowImportFields(!showImportFields)
  };

  // Styles for layout
  const sectionStyle = {
    margin: '5px 0 15px 0',
    padding: '10px',
    borderRadius: '5px',
  };

  const handleExecution = async () => {
    try {
      setAgentExecutionStatus("running"); // Set status to running
      const response = await executePromptConstructionAgent(
        question, databaseSchema, demonstrations, promptConstructionTemplate, promptConstructionModel);
      setGeneratedPrompt(response.prompt_text);
      setGeneratedSQL(response.prompt_result);
      setAgentExecutionStatus("completed"); // Set status to completed
    } catch (error) {
      console.error("Error executing Prompt Construction Agent:", error);
      setAgentExecutionStatus("failed"); // Set status to failed
    }
  };

  // Execute the agent when the promptAgentTrigger changes
  useEffect(() => {
    if (promptAgentTrigger) {
      handleExecution();
    }
  }, [promptAgentTrigger]);

  return (
    <div className="agent-tab-container" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', margin: '0px 0' }}>
        <img src={iconSrc} alt={`${selectedAgent.name} icon`} style={{ marginRight: '10px', width: '20px', height: '20px' }} />
        <h4 style={{ display: 'inline'}}>{selectedAgent.name}</h4>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '20px' }}>
        <div className="left-half" style={{ width: '50%' }}>
          <Card
            style={sectionStyle}
            elevation={Elevation.TWO}
          >
            <h4>Agent Inputs</h4>
            <FormGroup label="Question" labelFor="question-input">
              <InputGroup id="question-input" placeholder="Enter question" value={question} onChange={e => setQuestion(e.target.value)} />
            </FormGroup>
            <FormGroup label="Database" labelFor="database-input">
              <InputGroup id="database-input" placeholder="Enter database" value={database} onChange={e => setDatabase(e.target.value)} />
            </FormGroup>
            <FormGroup>
              <Button 
                text="Context Information from User-Defined-Agent" 
                onClick={toggleImportFields} 
                intent="primary" 
                style={{ marginBottom: '10px' }}
                size="small"
              />
              {showImportFields && (
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <div style={{ flex: 1, marginRight: '10px' }}>
                    <FormGroup label="Database Schema" labelFor="database-schema">
                      <TextArea 
                        id="database-schema" 
                        style={{ height: '130px', overflowY: 'auto' }} 
                        minrows={50} fill={true} 
                        placeholder="Enter database schema" 
                        value={databaseSchema} 
                        onChange={e => setDatabaseSchema(e.target.value)}  
                      />
                    </FormGroup>
                  </div>
                  <div style={{ flex: 1 }}>
                    <FormGroup label="Demonstrations" labelFor="demonstrations">
                      <TextArea 
                        id="demonstrations" 
                        style={{ height: '130px', overflowY: 'auto' }} 
                        minrows={50} fill={true} 
                        placeholder="Enter demonstrations" 
                        value={demonstrations} 
                        onChange={e => setDemonstrations(e.target.value)}
                      />
                    </FormGroup>
                  </div>
                </div>
              )}
            </FormGroup>
          </Card>
          <Card style={{ margin: '10px 0', padding: '10px' }} elevation={Elevation.TWO}>
            <h4>Agent Settings</h4>
            <div style={{ display: 'flex', flexDirection: 'column', marginTop: '10px' }}>
                <div style={{ display: 'flex' }}>
                    <FormGroup label="Prompt Template" style={{ flex: 1, marginRight: '20px' }}>
                        <RadioGroup onChange={e => setPromptConstructionTemplate(e.target.value)} selectedValue={promptConstructionTemplate}>
                            <Radio label="Template 1" value="option_1" />
                            <Radio label="Template 2" value="option_2" />
                            <Radio label="Template 3" value="option_3" />
                        </RadioGroup>
                    </FormGroup>
                    <FormGroup label="LLM" style={{ flex: 1 }}>
                        <RadioGroup onChange={e => setPromptConstructionModel(e.target.value)} selectedValue={promptConstructionModel}>
                            <Radio label="GPT-4" value="gpt-4" />
                            <Radio label="GPT-4 Turbo" value="gpt-4-turbo" />
                            <Radio label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
                        </RadioGroup>
                    </FormGroup>
                </div>
            </div>
          </Card>
        </div>
        <Divider orientation="vertical" style={{ margin: '0 0px', height: 'auto' }} />
        <div className="right-half" style={{ width: '50%' }}>
          <Card
            style={sectionStyle}
            elevation={Elevation.TWO}
          >
            <h4>Agent Outputs</h4>
            <FormGroup label="Generated Prompt" labelFor="generated-prompt">
              <TextArea className="agent-tab-text-area" id="generated-prompt" style={{ height: '200px', overflowY: 'auto' }} minrows={50} fill={true} value={generatedPrompt} onChange={e => setGeneratedPrompt(e.target.value)} />
            </FormGroup>
            <FormGroup label="Generated SQL" labelFor="generated-SQL">
              {/* <InputGroup id="generated-SQL" value={generatedSQL} onChange={e => setGeneratedSQL(e.target.value)} fill={true} /> */}
              <TextArea className="agent-tab-text-area" id="generated-SQL" style={{ height: '70px', overflowY: 'auto' }} minrows={1} fill={true} value={generatedSQL} onChange={e => setGeneratedSQL(e.target.value)} />
            </FormGroup>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AgentTab;