import React, { useContext, useCallback } from 'react';

import Button from '../button/button.component';

import { logout } from '../../scripts/api';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './menu-dropdown.styles.scss';

const MenuDropdown = ({ toggleDropdown }) => {
  const { setCurrentUser } = useContext(CurrentUserContext);

  const logoutHandler = useCallback(async () => {
    const response = await logout();
    if (!response.ok)
      return;
    
    const { sessionUser } = await response.json();
    setCurrentUser(sessionUser);
  }, [setCurrentUser]);

  const refCallback = useCallback((dropdown) => {
    if (dropdown) dropdown.focus();
  }, []);

  return (
    <div
      className='menu-dropdown'
      title='dropdown'
      tabIndex='-1'
      ref={refCallback}
      onBlur={toggleDropdown}
    >
      <ul>
        <li className='noselect'><Button onClick={() => {}}>Edit Profile</Button></li>
        <li className='noselect'></li>
        <li className='noselect'><Button onClick={logoutHandler}>Logout</Button></li>
      </ul>
    </div>
  );
};

export default MenuDropdown;
