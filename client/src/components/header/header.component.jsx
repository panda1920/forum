import React, { useContext } from 'react';

import HeaderButton from '../header-button/header-button.component';

import './header.styles.scss';
import { ModalContext } from '../../contexts/modal/modal';

const Header = ({ id }) => {
  const { toggleSignup, toggleLogin } = useContext(ModalContext);

  return (
    <header id={id}>
      <div className='logo-section'>
        <HeaderButton className='logo' >MY LOGO</HeaderButton>
      </div>
      <div className='controls-section'>
        <HeaderButton className='signup' onClick={toggleSignup}>SIGNUP</HeaderButton>
        <HeaderButton className='login' onClick={toggleLogin}>LOGIN</HeaderButton>
      </div>
    </header>
  );
}

export default Header;