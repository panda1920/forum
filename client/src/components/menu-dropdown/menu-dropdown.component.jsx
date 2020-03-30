import React, { useContext } from 'react';

import Button from '../button/button.component';

import { logout } from '../../scripts/api';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './menu-dropdown.styles.scss';

const MenuDropdown = () => {
  const { setCurrentUser } = useContext(CurrentUserContext);

  const logoutHandler = async () => {
    const response = await logout();
    if (!response.ok)
      return;
    
    const { sessionUser } = await response.json()
    setCurrentUser(sessionUser);
  }

  return (
    <div className='menu-dropdown' title='dropdown'>
      <ul>
        <li className='noselect'><Button onClick={() => {}}>Edit Profile</Button></li>
        <li className='noselect'></li>
        <li className='noselect'><Button onClick={logoutHandler}>Logout</Button></li>
      </ul>
    </div>
  );
};

export default MenuDropdown;