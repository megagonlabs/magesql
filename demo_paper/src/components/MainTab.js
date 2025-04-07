import React from 'react';
import { Card, Elevation, Switch, Tag, Button } from '@blueprintjs/core';
import Diagram from './Diagram';
import { useAgent } from '../context/AgentContext';
import './MainTab.css';

const MainTab = ({ selectAgentTab })  => {
  const { agents, toggleAgentActive, selectAgent } = useAgent();

  // Prevent default to stop click from propagating from Switch
  const handleSwitchChange = (event, agentName) => {
    event.stopPropagation(); // Stop click event from propagating
    toggleAgentActive(agentName);
  };

  // null modifyAgent function
  const modifyAgent = (agentName) => {
    console.log(`Modify agent: ${agentName}`);
  };

  const handleModifyClick = (agentName) => {
    modifyAgent(agentName);
  };

  const cardStyle = {
    borderRadius: '5px',
  };

  return (
    <div className="main-tab">
      <div className="agents-cards">
        {agents.map((agent) => (
          <Card
            key={agent.name}
            interactive={true}
            elevation={Elevation.TWO}
            style={cardStyle}
          >
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <div // Container for agent name and tag
                onClick={() => agent.isActive && selectAgentTab(agent.name)}
                style={{ cursor: 'pointer', flex: 1 }}
              >
                <h5>{agent.name}</h5>
                <div style={{ marginBottom: '10px' }}>
                  <Tag
                    intent={agent.name === "Data Loader Agent" || agent.name === "Prompt Construction Agent" ? "success" : "primary"}
                    minimal={true}
                    round={true}
                  >
                    {agent.name === "Data Loader Agent" || agent.name === "Prompt Construction Agent" ? "Required" : "Optional"}
                  </Tag>
                </div>
              </div>
              <div // Container for the switch and potentially the modify button
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <Switch
                  checked={agent.isActive}
                  label={agent.isActive ? "Active" : "Inactive"}
                  disabled={agent.name === "Data Loader Agent" || agent.name === "Prompt Construction Agent"}
                  onChange={(event) => handleSwitchChange(event, agent.name)}
                />
                {/* {agent.name === "Demonstration Selection Agent" && (
                  <Button 
                    icon="edit"
                    text="Modify"
                    style={{ backgroundColor: 'white', color: 'black' }}
                    // stopPropagation={true}
                  />
                )} */}
              </div>
            </div>
          </Card>
        ))}
      </div>
      <Diagram agents={agents.filter(agent => agent.isActive)} selectAgentTab={selectAgentTab} />
    </div>
  );
};

export default MainTab;
