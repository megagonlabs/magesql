import React from 'react';
import { Alignment, Navbar, NavbarGroup, NavbarHeading, NavbarDivider } from "@blueprintjs/core";

const Header = ({ logo, title, version }) => {
  return (
    <Navbar>
      <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
        <NavbarGroup align={Alignment.CENTER}>
          <img src={logo} alt="Logo" style={{ height: '40px', marginRight: '20px' }} />
          <NavbarHeading style={{ fontWeight: 'bold' }}>{title}</NavbarHeading>
          <NavbarDivider />
          <div>Version: {version}</div>
        </NavbarGroup>
      </div>
    </Navbar>
  );
};

export default Header;