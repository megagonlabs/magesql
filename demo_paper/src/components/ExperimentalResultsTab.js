import React, { useMemo, useState, useEffect, useCallback } from 'react';
import { Card, Elevation, FormGroup, InputGroup, HTMLTable, TextArea } from "@blueprintjs/core";
import { useAgent } from '../context/AgentContext';
import './ExperimentalResultsTab.css';

const tableStyle = {
  width: '100%',
  border: '1px solid #d7d7d7',
  borderCollapse: 'collapse'
};

const ExperimentalResultsTab = ({ compareTrigger }) => {
  const {
    question,
    database,
    SQLForExecution, setSQLForExecution,
    executionResults=[],
    goldSQL, setGoldSQL,
    goldExecutionResults=[],
    isResultsSame,
    modifiedGeneratedResults=[],
    showComparedResults,
    setShowComparedResults,
    comparisonText,
    compareAndHighlightResults, // Use compare function from context
    
  } = useAgent();

  const [loadingComparison, setLoadingComparison] = useState(false); // To handle loading state when comparing results

  const handleCompareResults = useCallback(async () => {
    setLoadingComparison(true);
    try {
      await compareAndHighlightResults();
    } catch (error) {
      console.error("Error comparing results", error);
    } finally {
      setLoadingComparison(false);
    }
  }, [compareAndHighlightResults]);

  useEffect(() => {
    if (compareTrigger) {
      handleCompareResults(); // Trigger comparison if compareTrigger changes
    }
  }, [compareTrigger, handleCompareResults]);

  const renderResultsTable = (results) => {
  // If results is a string (likely an error message), show it in red
  if (typeof results === 'string') {
    return <p style={{ color: 'red' }}>{results}</p>;
  }
  
  // If results are empty, show the message in grey
  if (!results || results.length === 0 || !results[0]) {
    return <p style={{ color: 'grey' }}>The execution result is empty.</p>;
  }

    const tableHeaders = Object.keys(results[0]).filter(key => key !== '_style');
    return (
      <HTMLTable
        style={{ ...tableStyle, borderCollapse: 'collapse', margin: '0', padding: '0', fontSize: '12px' }}
        bordered={true}
      >
        <thead className='table-header'>
          <tr>
            {tableHeaders.map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => {
            const rowStyle = result._style === 'false_positive'
              ? { backgroundColor: '#ffe5e5' }
              : result._style === 'true_negative'
                ? { backgroundColor: '#e5ffe5' }
                : {};

            return (
              <tr key={index} style={rowStyle}>
                {tableHeaders.map((key, cellIndex) => (
                  <td key={cellIndex}>{result[key]}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </HTMLTable>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ marginBottom: '20px' }}>
        <FormGroup label="Question">
          <InputGroup readOnly value={question} />
        </FormGroup>
        <FormGroup label="Database">
          <InputGroup readOnly value={database} />
        </FormGroup>
      </div>
      <div style={{ display: 'flex', flexGrow: 1, gap: '20px', width: '100%' }}>
        <div className="left-half" style={{ flex: 1 }}>
          <Card elevation={Elevation.TWO}>
            <h4 style={{ marginTop: '0' }}>Generated SQL & Execution</h4>
            <FormGroup label="Generated SQL">
              <TextArea id="generated-sql" style={{ height: '70px', overflowY: 'auto' }} rows={1} fill={true} value={SQLForExecution || ''} onChange={e => setSQLForExecution(e.target.value)} />
            </FormGroup>
            <FormGroup label="Execution Results">
              {showComparedResults ? renderResultsTable(modifiedGeneratedResults) : renderResultsTable(executionResults)}
            </FormGroup>
          </Card>
        </div>
        <div className="right-half" style={{ flex: 1 }}>
          <Card elevation={Elevation.TWO}>
            <h4 style={{ marginTop: '0' }}>Gold SQL & Execution</h4>
            <FormGroup label="Gold SQL">
              <TextArea id="gold-sql" style={{ height: '70px', overflowY: 'auto' }} rows={1} fill={true} value={goldSQL || ''} onChange={e => setGoldSQL(e.target.value)} />
            </FormGroup>
            <FormGroup label="Execution Results">
              {renderResultsTable(goldExecutionResults)}
            </FormGroup>
          </Card>
        </div>
      </div>
      {showComparedResults && (
        <div style={{ marginTop: '20px' }}>
          <p style={{ color: isResultsSame ? 'green' : 'red' }}>
            {comparisonText || (isResultsSame ? "The execution results are the same." : "The execution results are different.")}
          </p>
        </div>
      )}
    </div>
  );
};

export default ExperimentalResultsTab;
