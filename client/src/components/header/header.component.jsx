import React, { useContext } from 'react';

import Button from '../button/button.component';

import './header.styles.scss';
import { ModalContext } from '../../contexts/modal/modal';

const Header = ({ id }) => {
  const { toggleSignup, toggleLogin } = useContext(ModalContext);

  return (
    <header id={id}>
      <div className='logo-section'>
        <Button
          className='header-button button-logo'
        >
          MYFORUMAPP
        </Button>
      </div>
      <div className='controls-section'>
        <Button
          className='header-button button-signup'
          onClick={toggleSignup}
        >
          SIGNUP
        </Button>
        <Button
          className='header-button button-login'
          onClick={toggleLogin}
        >
          LOGIN
        </Button>
      </div>
    </header>
  );
}

export default Header;