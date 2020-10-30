import React, { useContext, useCallback } from 'react';

import Button from '../button/button.component';

import { logout } from '../../scripts/api';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './menu-dropdown.styles.scss';
import BlockText from '../block-text/block-text.component';

const MenuDropdown = ({ toggleDropdown }) => {
  const { displayName, userName, setCurrentUser } = useContext(CurrentUserContext);

  const logoutHandler = useCallback(async () => {
    const response = await logout();
    if (!response.ok)
      return;
    
    const { sessionUser } = await response.json();
    setCurrentUser(sessionUser);
    toggleDropdown();
  }, [setCurrentUser, toggleDropdown]);

  const refCallback = useCallback((dropdown) => {
    // focus when this component first renders
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
        <li className='noselect'>
          <div className='dropdown-userinfo'>
            <BlockText className='dropdown-username'>{displayName}</BlockText>
            <BlockText className='dropdown-email'>{userName}</BlockText>
          </div>
        </li>
        <li className='noselect separator'></li>
        <li className='noselect'>
          <BlockText><Button onClick={() => {}}>Edit Profile</Button></BlockText>
        </li>
        <li className='noselect'>
          <BlockText><Button onClick={logoutHandler}>Logout</Button></BlockText>
        </li>
      </ul>
    </div>
  );
};

export default MenuDropdown;
