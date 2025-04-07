import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useAgent } from '../context/AgentContext';

const getIconPath = (iconName) => {
  // Assuming your build process copies the src/icons directory to the public folder
  // Adjust the path as necessary based on your project's structure
  return `${process.env.PUBLIC_URL}/icons/${iconName}.svg`;
};

const Diagram = ({ agents, selectAgentTab }) => {
  const d3Container = useRef(null);

  // console.log('selectAgentTab is:', selectAgentTab);

  useEffect(() => {
    if (d3Container.current && agents && agents.length) {
      // Clear previous SVG content
      d3.select(d3Container.current).selectAll('*').remove();

      // Set diagram dimensions
      const width = 1000; // Width of the diagram container
      const height = 300;  // Height of the diagram container
      const nodeRadius = 25; // Radius of the nodes
      const offset = 120; // Vertical offset for the "Demonstration Selection Agent"
      const smallCircleRadius = 18; // Radius of the small circle

      // Define the arrow marker for indicating direction
      const svg = d3.select(d3Container.current).append('svg')
        .attr('width', width)
        .attr('height', height);

      svg.append('defs').append('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 10) // Arrowhead position at the edge of the node
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', 'black');

      svg.append('defs').append('marker')
        .attr('id', 'arrow-orange')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 10)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', 'orange');

      const activeAgents = agents.filter(agent => agent.isActive);
      
      // Calculate the number of nodes that should affect the x position (excluding inactive "Demonstration Selection Agent")
      const numberOfActiveAgents = activeAgents.filter(agent => agent.name !== "Demonstration Selection Agent").length;

      // Find the index of the "Prompt Construction Agent"
      const promptAgentIndex = activeAgents.findIndex(agent => agent.name === "Prompt Construction Agent");
      const promptAgentExists = promptAgentIndex >= 0;
      const demoAgentIndex = activeAgents.findIndex(agent => agent.name === "Demonstration Selection Agent");
      const demoAgentExists = demoAgentIndex >= 0;

      let valid_i = 0; // Counter for active agents to correctly calculate x positions
      const agentPositions = activeAgents.map((agent, i) => {
        let x;
        let y = height * 0.7; // Horizontal line y position
        if (agent.name !== "Demonstration Selection Agent") {
          valid_i += 1;
          x = (width / (numberOfActiveAgents + 1)) * valid_i;
        } else {
          x = width / 2; // x position for "Demonstration Selection Agent"
          y -= offset; // y position for "Demonstration Selection Agent"
        }
        return { ...agent, x, y };
      });

      let demoAgent, promptAgent;
      if (demoAgentExists && promptAgentExists) {
        // align demoAgent position to same x with promptAgent
        demoAgent = agentPositions[demoAgentIndex];
        promptAgent = agentPositions[promptAgentIndex];
        demoAgent.x = promptAgent.x;
      }


      const iconPath = iconName => `/icons/${iconName}.svg`;

      // Create groups for each agent
      const nodeGroups = svg.selectAll('.node')
        .data(agentPositions)
        .enter().append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .on('click', (event, d) => {
          if (d.isActive) selectAgentTab(d.name);
        });

      // Add circles to each node group
      nodeGroups.append('circle')
        .attr('r', nodeRadius)
        .attr('fill', 'white')
        // .attr('fill', d => {
        //   if (d.name === "Data Loader Agent" || d.name === "Prompt Construction Agent") {
        //     return '#90ee90';
        //   } else if (d.name === "Demonstration Selection Agent") {
        //     return '#ffffe0';
        //   } else {
        //     return 'white';
        //   }
        // })
        .attr('stroke', 'black')
        // .attr('stroke', d => d.name === "Demonstration Selection Agent" ? 'orange' : 'black')
        .attr('stroke-width', '3');

      nodeGroups.append('circle')
        .attr('r', smallCircleRadius)
        // .attr('fill', '#106ba3')
        // .attr('fill', '#2D72D2')
        .attr('fill', d => {
          if (d.name === "Data Loader Agent" || d.name === "Prompt Construction Agent") {
            return 'green'; // Green for specific agents
          } else if (d.name === "Demonstration Selection Agent") {
            return 'orange'; // Yellow for Demonstration Selection Agent
          } else {
            return '#2D72D2'; // Default color
          }
        })
        .attr('stroke', 'black')
        // .attr('stroke', d => d.name === "Demonstration Selection Agent" ? 'orange' : 'black')
        .attr('stroke-width', '2');

      // Add mouseover and mouseout events to the group to affect both circles
      nodeGroups
        .on('mouseover', function() {
          const currentAgent = d3.select(this).datum();
          let strokeColor;
          if (currentAgent.name === "Data Loader Agent" || currentAgent.name === "Prompt Construction Agent") {
            strokeColor = 'green'; // Green for specific agents
          } else if (currentAgent.name === "Demonstration Selection Agent") {
            strokeColor = 'orange'; // Orange for Demonstration Selection Agent
          } else {
            strokeColor = '#2D72D2'; // Default color (blue)
          }
          d3.select(this).selectAll('circle')
            .transition()
            .duration(100)
            // .attr('stroke', '#106ba3')
            // .attr('stroke', '#2D72D2')
            .attr('stroke', strokeColor)
            .attr('stroke-width', '5');
        })
        .on('mouseout', function() {
          d3.select(this).selectAll('circle')
            .transition()
            .duration(100)
            .attr('stroke', 'black')
            .attr('stroke-width', '2');
        });
      
      // Append an SVG image for each node group based on the agent's icon name
      nodeGroups.append('image')
        .attr('xlink:href', d => iconPath(d.icon))
        .attr('width', 20)
        .attr('height', 20)
        .attr('x', -10)
        .attr('y', -10)
        .style('filter', 'invert(100%)'); // Inverts the colors
    
      
      // Add labels to each node group
      nodeGroups.append('text')
        .attr('y', d => d.name === "Demonstration Selection Agent" ? -(nodeRadius + 15) : nodeRadius + 20)
        .attr('text-anchor', 'middle')
        .text(d => d.name.replace(' Agent', ''))
        .style('font-size', '15px');

      // Draw the lines
      let prevX = 0;  // Keep track of the x position of the last node in the main line
      agentPositions.forEach((agent, i) => {
        if (agent.name !== "Demonstration Selection Agent") {
          if (prevX > 0) {
            // Draw a line from the previous node to this one
            svg.append('line')
              .attr('x1', prevX)
              .attr('y1', height * 0.7)
              .attr('x2', agent.x - nodeRadius)  // Subtract nodeRadius to prevent overlap
              .attr('y2', height * 0.7)
              .attr('stroke', 'black')
              .attr('marker-end', 'url(#arrow)')
              .attr('stroke-width', '2');
          }
          prevX = agent.x + nodeRadius;  // Update prevX to the right edge of the current node
        }
      });

      // Draw the line from "Demonstration Selection Agent" if active
      if (demoAgentExists && promptAgentExists) {
        // Draw a line from the demonstration agent to the prompt construction agent
        svg.append('line')
          .attr('x1', demoAgent.x)
          .attr('y1', demoAgent.y + nodeRadius)
          .attr('x2', promptAgent.x)
          .attr('y2', promptAgent.y - nodeRadius)
          // .attr('stroke', 'black')
          .attr('stroke', 'orange')
          .attr('marker-end', 'url(#arrow-orange)')
          // .attr('marker-end', 'url(#arrow)')
          .attr('stroke-width', '2');
      }
    }
  }, [agents, selectAgentTab]);

  return <div ref={d3Container}></div>;
};

export default Diagram;