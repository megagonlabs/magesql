import React, { useState } from 'react';
import { Button, FormGroup, InputGroup, Intent, Callout } from "@blueprintjs/core";
import { Form } from '@blueprintjs/icons';
import './ConnectionForm.css';

const ConnectionForm = () => {
  const [host, setHost] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('Not Connected');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false); // Added missing state

  const handleConnectionClick = () => {
    if (isConnected) {
      setIsConnected(false);
      setConnectionStatus('Not Connected');
    } else {
      setIsConnecting(true);
      setConnectionStatus('Connecting...');

      setTimeout(() => {
        setIsConnecting(false);
        setIsConnected(true);
        setConnectionStatus('Connected');
      }, 1500); // Delay of 1.5 seconds
    }
  };

  return (
    <div className="connection-form">
      <h3>Connect to Database</h3>
      <FormGroup label="Host" labelFor="host-input" labelClassName="label" className="form-group-custom">
        <InputGroup 
          id="host-input"
          placeholder="Enter host..."
          value={host}
          onChange={(e) => setHost(e.target.value)}
          disabled={isConnected}
          className="input-group"
        />
      </FormGroup>
      <FormGroup label="Username" labelFor="username-input" labelClassName="label">
        <InputGroup
          id="username-input"
          placeholder="Enter username..."
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={isConnected}
          className="input-group"
        />
      </FormGroup>
      <FormGroup label="Password" labelFor="password-input" labelClassName="label">
        <InputGroup 
          id="password-input"
          placeholder="Enter password..."
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isConnected}
          className="input-group"
        />
      </FormGroup>
      <div className="connection-actions">
        <Button 
          text={isConnected ? "Disconnect" : "Connect"}
          intent={isConnected ? Intent.DANGER : Intent.PRIMARY}
          onClick={handleConnectionClick}
        />
        <span className={`connection-status ${isConnected ? 'connected' : isConnecting ? 'connecting' : 'disconnected'}`}>
        {connectionStatus}
      </span>
      </div>
    </div>
  );
};

export default ConnectionForm;
