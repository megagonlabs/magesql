import React, { useState, useEffect } from 'react';
import { Card, Elevation, FormGroup, InputGroup, Slider, TextArea, Divider } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import { executeDemonstrationSelectionAgent } from '../api/agentApi';

const getIconPath = (iconName) => {
  return `${process.env.PUBLIC_URL}/icons/${iconName}.svg`;
};

const DemonstrationSelectionAgent = () => {
  const {
    question, setQuestion,
    demonstrations, setDemonstrations,
    selectedAgent,
    agentExecutionStatus, setAgentExecutionStatus,
    demonstrationAgentTrigger,
    numDemonstrations, setNumDemonstrations,
  } = useAgent();

  // Safe access to selectedAgent properties
  const iconSrc = selectedAgent ? getIconPath(selectedAgent.icon) : '';

  // Styles for layout
  const sectionStyle = {
    margin: '5px 0 15px 0',
    padding: '10px',
    borderRadius: '5px',
  };

  const handleExecution = async () => {
    try {
      setAgentExecutionStatus("running"); // Set status to running
      const response = await executeDemonstrationSelectionAgent(
        question, numDemonstrations
      );
      setDemonstrations(response.demonstrations); // Assuming backend returns demonstration_text
      setAgentExecutionStatus("completed"); // Set status to completed
    } catch (error) {
      console.error("Error executing Demonstration Selection Agent:", error);
      setAgentExecutionStatus("failed"); // Set status to failed
    }
  };

  // Execute the agent when the demonstrationAgentTrigger changes
  useEffect(() => {
    if (demonstrationAgentTrigger) {
      handleExecution();
    }
  }, [demonstrationAgentTrigger]);

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
          </Card>
          <Card
            style={{ margin: '10px 0', padding: '10px' }}
            elevation={Elevation.TWO}
          >
            <h4>Agent Settings</h4>
            <FormGroup label="Number of Demonstrations">
              <Slider
                min={1}
                max={10}
                stepSize={1}
                labelStepSize={1}
                value={numDemonstrations}
                onChange={(value) => setNumDemonstrations(value)}
              />
            </FormGroup>
          </Card>
        </div>
        <Divider orientation="vertical" style={{ margin: '0 0px', height: 'auto' }} />
        <div className="right-half" style={{ width: '50%' }}>
          <Card
            style={sectionStyle}
            elevation={Elevation.TWO}
          >
            <h4>Agent Outputs</h4>
            <FormGroup label="Generated Demonstrations" labelFor="generated-demonstrations">
              <TextArea className="agent-tab-text-area" id="generated-demonstrations" style={{ height: '200px', overflowY: 'auto' }} rows={5} fill={true} value={demonstrations} onChange={e => setDemonstrations(e.target.value)} />
            </FormGroup>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DemonstrationSelectionAgent;
