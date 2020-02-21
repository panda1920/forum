import React from 'react';

import HeaderButton from '../header-button/header-button.component';

import './header.styles.scss';

const Header = ({ id }) => {
  return (
    <header id={id}>
      <div className='logo-section'>
        <HeaderButton className='logo'>MY LOGO</HeaderButton>
      </div>
      <div className='controls-section'>
        <HeaderButton className='signup'>SIGNUP</HeaderButton>
        <HeaderButton className='login'>LOGIN</HeaderButton>
      </div>
    </header>
  );
}

export default Header;