import React, { useState, useEffect } from 'react';
import { Button, Card, Elevation, FormGroup, InputGroup, Radio, RadioGroup, TextArea, Divider, H3, Checkbox } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import { executeErrorCorrectionAgent } from '../api/agentApi';

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
    correctionPrompt, setCorrectionPrompt,
    correctedSQL, setCorrectedSQL,
    selectedAgent,
    agentExecutionStatus, setAgentExecutionStatus,
    executePipeline,
    correctionModel, setCorrectionModel,
    correctionAgentTrigger, setCorrectionAgentTrigger,
  } = useAgent();

  const [errorCorrectionRulesGroup, setErrorCorrectionRulesGroup] = useState([1, 2, 3]);

  // Safe access to selectedAgent properties
  const iconSrc = selectedAgent ? getIconPath(selectedAgent.icon) : '';

  // Handle database selection (simulate fetching schema)
  const handleDatabaseSelect = async (e) => {
    const dbName = e.target.value;
    setDatabase(dbName);
    // const schema = await fetchDatabaseSchema(dbName);
  };

  // Styles for layout
  const sectionStyle = {
    margin: '5px 0 15px 0',
    padding: '10px',
    borderRadius: '5px',
  };

  // Handle checkbox changes for rules groups
  const handleCheckboxChange = (groupNumber) => {
    setErrorCorrectionRulesGroup((prevGroups) =>
      prevGroups.includes(groupNumber)
        ? prevGroups.filter((g) => g !== groupNumber)  // Remove if already selected
        : [...prevGroups, groupNumber]                 // Add if not selected
    );
  };

  const handleExecution = async () => {
    try {
      setAgentExecutionStatus("running"); // Set status to running
      const response = await executeErrorCorrectionAgent(
        question,
        generatedSQL,
        databaseSchema,
        errorCorrectionRulesGroup,
        correctionModel
      );
      setCorrectionPrompt(response.prompt_text);
      setCorrectedSQL(response.prompt_result);
      setAgentExecutionStatus("completed"); // Set status to completed
    } catch (error) {
      console.error("Error executing Error Correction Agent:", error);
      setAgentExecutionStatus("failed"); // Set status to failed
    }
  };

  // Execute the agent when the promptAgentTrigger changes
  useEffect(() => {
    if (correctionAgentTrigger) {
      handleExecution();
    }
  }, [correctionAgentTrigger]);

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
              <InputGroup id="database-input" placeholder="Enter database" value={database} onChange={handleDatabaseSelect} />
            </FormGroup>
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
            <FormGroup label="Generated SQL">
              {/* <InputGroup readOnly defaultValue={generatedSQL} /> */}
              <TextArea id="generated-sql" style={{ height: '70px', overflowY: 'auto' }} minrows={1} fill={true} value={generatedSQL} readOnly />
            </FormGroup>
          </Card>
          <Card style={{ margin: '10px 0', padding: '10px' }} elevation={Elevation.TWO}>
            <h4>Agent Settings</h4>
            <div style={{ display: 'flex', flexDirection: 'column', marginTop: '10px' }}>
                <div style={{ display: 'flex' }}>
                  <FormGroup label="Error Correction Rules Group" style={{ flex: 1, marginRight: '20px' }}>
                    {/* Change to checkboxes */}
                    <Checkbox
                      label="Rules Group 1"
                      checked={errorCorrectionRulesGroup.includes(1)}
                      onChange={() => handleCheckboxChange(1)}
                    />
                    <Checkbox
                      label="Rules Group 2"
                      checked={errorCorrectionRulesGroup.includes(2)}
                      onChange={() => handleCheckboxChange(2)}
                    />
                    <Checkbox
                      label="Rules Group 3"
                      checked={errorCorrectionRulesGroup.includes(3)}
                      onChange={() => handleCheckboxChange(3)}
                    />
                  </FormGroup>
                  <FormGroup label="LLM" style={{ flex: 1 }}>
                    <RadioGroup onChange={e => setCorrectionModel(e.target.value)} selectedValue={correctionModel}>
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
            <FormGroup label="Generated Error Correction Prompt" labelFor="generated-correction-prompt">
              <TextArea className="agent-tab-text-area" id="generated-correction-prompt" style={{ height: '200px', overflowY: 'auto' }} minrows={50} fill={true} value={correctionPrompt} onChange={e => setCorrectionPrompt(e.target.value)} />
            </FormGroup>
            <FormGroup label="Generated Corrected SQL" labelFor="generated-corrected-sql">
              {/* <InputGroup id="generated-SQL" value={generatedSQL} onChange={e => setGeneratedSQL(e.target.value)} fill={true} /> */}
              <TextArea className="agent-tab-text-area" id="generated-corrected-sql" style={{ height: '70px', overflowY: 'auto' }} minrows={1} fill={true} value={correctedSQL} onChange={e => setCorrectedSQL(e.target.value)} />
            </FormGroup>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AgentTab;