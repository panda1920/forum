import React, { useContext, useState, useCallback } from 'react';

import Button from '../button/button.component';
import Portrait from '../portrait/portrait.component';
import MenuDropdown from '../menu-dropdown/menu-dropdown.component';

import { ModalContext } from '../../contexts/modal/modal';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './header.styles.scss';

const Header = () => {
  const { toggleSignup, toggleLogin } = useContext(ModalContext);
  const { imageUrl, isLoggedin } = useContext(CurrentUserContext);
  const [ isDropdownVisible, setIsDropdownVisible ] = useState(false);

  const toggleDropdown = useCallback(() => {
    setIsDropdownVisible(visibleState => !visibleState);
  }, []);

  const renderControlSectionBasedOnLoggedinState= () => {

    if ( isLoggedin() )
      return (
        <div className='controls-section'>
          <Button
            className='button-portrait'
            onClick={toggleDropdown}
          >
            <Portrait title='header portrait' imageUrl={imageUrl} />
            { isDropdownVisible ? <MenuDropdown toggleDropdown={toggleDropdown} /> : null }
          </Button>
        </div>
      );
    else
      return (
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
      );
  };

  return (
    <header id='header' title='header'>
      <div className='logo-section'>
        <Button
          className='header-button button-logo'
        >
          MYFORUMAPP
        </Button>
      </div>
      { renderControlSectionBasedOnLoggedinState() }
    </header>
  );
};

export default Header;