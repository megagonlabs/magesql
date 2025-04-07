import React, { useState, useEffect } from 'react';
import { Button, Card, Elevation, FormGroup, InputGroup, Radio, RadioGroup, TextArea, Divider, H3 } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import PromptConstructionAgent from '../agents/PromptConstructionAgent';
import ErrorCorrectionAgent from '../agents/ErrorCorrectionAgent';
import DemonstrationSelectionAgent from '../agents/DemonstrationSelectionAgent';
import DatabaseRoutingAgent from '../agents/DatabaseRoutingAgent';
import './AgentTab.css';

// Mock function to simulate fetching database schema
const fetchDatabaseSchema = async (databaseName) => {
  return `Schema for ${databaseName}`;
};

const getIconPath = (iconName) => {
  return `${process.env.PUBLIC_URL}/icons/${iconName}.svg`;
};

const AgentTab = () => {
  const { selectedAgent } = useAgent();

  // // Early return if no agent is selected
  // if (!selectedAgent) {
  //   return <div>Please select an agent.</div>;
  // }

  // useEffect(() => {
  //   // Reset or set defaults when the selected agent changes
  //   switch (selectedAgent?.name) {
  //     case 'Prompt Construction Agent':
  //       // setDatabase("flight_2"); // Example default value
  //       // Set other defaults or reset states as needed
  //       break;
  //     case 'Error Correction Agent':
  //       // Set defaults or reset states specific to Error Correction Agent
  //       break;
  //     // Add other agents as needed
  //     default:
  //       break;
  //   }
  // }, [selectedAgent]);

  // Render based on selectedAgent.name
  const renderAgentSpecificInputs = () => {
    switch (selectedAgent?.name) {
      case 'Prompt Construction Agent':
        return (
          <React.Fragment>
            {/* Inputs specific to Prompt Construction Agent */}
          </React.Fragment>
        );
      case 'Error Correction Agent':
        return (
          <React.Fragment>
            {/* Inputs specific to Error Correction Agent */}
          </React.Fragment>
        );
      case 'Demonstration Selection Agent':
        return (
          <React.Fragment>
            {/* Inputs specific to Demonstration Selection Agent */}
          </React.Fragment>
        );
      case 'Database Routing Agent':
        return (
          <React.Fragment>
            {/* Inputs specific to Database Routing Agent */}
          </React.Fragment>
        );
      // Add cases for other agents as needed
      default:
        return null;
    }
  };

  const renderAgentComponent = () => {
    console.log("Selected agent state in renderAgentComponent function: ", selectedAgent);
    if (!selectedAgent) {
      // This check effectively handles the scenario where no agent is selected
      // and displays a message prompting the user to select an agent.
      return <div>Please select an active agent.</div>;
    }
    switch (selectedAgent.name) {
      case 'Prompt Construction Agent':
        return <PromptConstructionAgent />;
      case 'Error Correction Agent':
        return <ErrorCorrectionAgent />;
      case 'Demonstration Selection Agent':
        return <DemonstrationSelectionAgent />;
      case 'Database Routing Agent':
        return <DatabaseRoutingAgent />;
      default:
        return <div>Agent component not found.</div>;
    }
  };

  return (
    <div>
      {renderAgentComponent()}
    </div>
  );
};

export default AgentTab;