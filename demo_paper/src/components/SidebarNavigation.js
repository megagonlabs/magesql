import React from 'react';
import { Menu, MenuItem } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import './SidebarNavigation.css';

const SidebarNavigation = ({ selectAgentTab }) => {
  const { agents } = useAgent();

  return (
    <Menu>
      {agents.map((agent) => (
        <MenuItem
          className='menu-item-custom'
          key={agent.name} 
          text={agent.name} 
          icon={agent.icon}
          onClick={() => agent.isActive && selectAgentTab(agent.name)}
          labelElement={<span className={agent.isActive ? "active" : "inactive"}>{agent.isActive ? "Active" : "Inactive"}</span>}
        />
      ))}
    </Menu>
  );
};
export default SidebarNavigation;