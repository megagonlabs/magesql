import React, { useEffect } from 'react';
import { Card, Elevation, FormGroup, InputGroup, Divider } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import { executeDatabaseRoutingAgent } from '../api/agentApi';

const getIconPath = (iconName) => {
  return `${process.env.PUBLIC_URL}/icons/${iconName}.svg`;
};

const DatabaseRoutingAgent = () => {
  const {
    question, setQuestion,
    database, setDatabase,
    selectedAgent,
    agentExecutionStatus, setAgentExecutionStatus,
    databaseRoutingAgentTrigger,
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
      const response = await executeDatabaseRoutingAgent(question);
      setDatabase(response.db_id); // Assuming backend returns database identifier
      setAgentExecutionStatus("completed"); // Set status to completed
    } catch (error) {
      console.error("Error executing Database Routing Agent:", error);
      setAgentExecutionStatus("failed"); // Set status to failed
    }
  };

  // Execute the agent when the databaseRoutingAgentTrigger changes
  useEffect(() => {
    if (databaseRoutingAgentTrigger) {
      handleExecution();
    }
  }, [databaseRoutingAgentTrigger]);

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
        </div>
        <Divider orientation="vertical" style={{ margin: '0 0px', height: 'auto' }} />
        <div className="right-half" style={{ width: '50%' }}>
          <Card
            style={sectionStyle}
            elevation={Elevation.TWO}
          >
            <h4>Agent Outputs</h4>
            <FormGroup label="Selected Database" labelFor="selected-database">
              <InputGroup id="selected-database" placeholder="Database will be displayed here" value={database} onChange={e => setDatabase(e.target.value)} />
            </FormGroup>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DatabaseRoutingAgent;
