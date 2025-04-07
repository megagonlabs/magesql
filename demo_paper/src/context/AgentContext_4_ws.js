// This file defines the context and a provider that wraps the part of the application where the context is needed, making the states and their setters available globally.

import React, { createContext, useContext, useState, useCallback } from 'react';

const AgentContext = createContext();

export const useAgent = () => useContext(AgentContext);

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
    const [agents, setAgents] = useState(initialAgents);

    const [question, setQuestion] = useState("Find the abbreviation and country of five airline that have fewest number of flights?");
    const [database, setDatabase] = useState("flight_2");
    const [databaseSchema, setDatabaseSchema] = useState(
`CREATE TABLE 'airlines' (
	uid INTEGER PRIMARY KEY, 
	Airline TEXT, 
	Abbreviation TEXT, 
	Country TEXT
)

CREATE TABLE 'airports' (
	City TEXT, 
	AirportCode TEXT PRIMARY KEY, 
	AirportName TEXT, 
	Country TEXT, 
	CountryAbbrev TEXT
)

CREATE TABLE 'flights' (
	Airline INTEGER, 
	FlightNo INTEGER, 
	SourceAirport TEXT, 
	DestAirport TEXT, 
	PRIMARY KEY(Airline, FlightNo),
	FOREIGN KEY (SourceAirport) REFERENCES airports(AirportCode),
	FOREIGN KEY (DestAirport) REFERENCES airports(AirportCode)
)
`
    );
    const [goldSQL, setGoldSQL] = useState('');
    const [demonstrations, setDemonstrations] = useState(
`Question: Find the number of users called Michelle
SQL: SELECT COUNT ( DISTINCT name ) FROM USER WHERE name  =  "Michelle";

Question: Find the total number of reviews written in March
SQL: SELECT COUNT ( DISTINCT text ) FROM review WHERE MONTH  =  "March";

Question: Find the number of tips written in each month
SQL: SELECT COUNT ( DISTINCT text )  ,  MONTH FROM tip GROUP BY MONTH;

Question: Find the business which has the most number of categories
SQL: SELECT t1.name FROM category AS t2 JOIN business AS t1 ON t2.business_id  =  t1.business_id GROUP BY t1.name ORDER BY COUNT ( DISTINCT t2.category_name ) DESC LIMIT 1;

Question: What is the number of movies that " Brad Pitt " acts in per year ?
SQL: SELECT COUNT ( DISTINCT t2.title  )  ,  t2.release_year FROM CAST AS t3 JOIN actor AS t1 ON t3.aid  =  t1.aid JOIN movie AS t2 ON t2.mid  =  t3.msid WHERE t1.name  =  "Brad Pitt" GROUP BY t2.release_year;`
    );
    const [generatedSQL, setGeneratedSQL] = useState(
`SELECT abbreviation, country FROM airlines ORDER BY number_of_flights ASC LIMIT 5;`
// `SELECT t1.Abbreviation, t1.Country FROM airlines AS t1 JOIN flights AS t2 ON t1.uid = t2.Airline GROUP BY t1.uid ORDER BY COUNT(t2.FlightNo) ASC LIMIT 5;`
    );
    const [generatedCorrectedSQL, setGeneratedCorrectedSQL] = useState(
`SELECT t1.Abbreviation, t1.Country FROM airlines AS t1 JOIN flights AS t2 ON t1.uid = t2.Airline GROUP BY t1.uid, t1.Abbreviation, t1.Country ORDER BY COUNT(t2.FlightNo) ASC LIMIT 5;`
    );


    // Toggle the active state of an agent
    const toggleAgentActive = (agentName) => {
        setAgents(agents.map(agent =>
            agent.name === agentName ? { ...agent, isActive: !agent.isActive } : agent
        ));
    };

    // Reset agent statuses to default
    const resetAgentStatuses = () => {
        setAgents(initialAgents);
    };

    const [pipelineStatus, setPipelineStatus] = useState("idle"); // "idle", "running", "completed"

    const executePipeline = async () => {
        setPipelineStatus("running");
        console.log("Executing pipeline with active agents.");
        // Simulate a long-running operation
        setTimeout(() => {
            console.log("Pipeline execution completed.");
            setPipelineStatus("completed");
          // Reset the status back to idle after showing 'completed' for a short period
            setTimeout(() => setPipelineStatus("idle"), 2000);
        }, 6000);
    };


    // Function to execute the selected agent
    const executeSelectedAgent = () => {
        console.log('Executing', selectedAgent.name);
    };

    const [executionResults, setExecutionResults] = useState([]);
    // Execute SQL (Placeholder for actual functionality)
    const executeSQL = () => {
        const newResults = [{ id: 1, result: 'Example SQL execution result' }];
        setExecutionResults(newResults);
    };

    // Placeholder function to handle saving results
    const handleSaveResults = () => {
        console.log("Saving execution results...");
    };


    const value = {
        selectedAgent, setSelectedAgent,
        agents, setAgents,
        question, setQuestion,
        database, setDatabase,
        databaseSchema, setDatabaseSchema,
        goldSQL, setGoldSQL,
        demonstrations, setDemonstrations,
        generatedSQL, setGeneratedSQL,
        generatedCorrectedSQL, setGeneratedCorrectedSQL,
        pipelineStatus, setPipelineStatus,
        executionResults, setExecutionResults,
        toggleAgentActive, resetAgentStatuses,
        handleSaveResults, executeSelectedAgent, executeSQL, 
        executePipeline, 
    };

    return (
        <AgentContext.Provider value={value}>
            {children}
        </AgentContext.Provider>
    );
};
