import React, { useContext } from 'react';
import { Redirect } from 'react-router-dom';

import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import ProfileFieldText from '../../components/profile-field/profile-field-text.component';
import ProfilePasswordText from '../../components/profile-field/profile-field-password.component';
import Spinner from '../../components/spinner/spinner.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './user-profile-page.styles.scss';

const UserProfile = () => {
  const { isLoggedin, beforeFetch, displayName } = useContext(CurrentUserContext);

  if (beforeFetch)
    return <Spinner />;
  if (!isLoggedin())
    return <Redirect to='/' />;

  return (
    <div className='user-profile-page'>
      { createBreadCrumbs() }
      <div className='user-profile-page-info'>
        <h1>User Profile</h1>
      </div>
      <div className='user-profile-page-fields'>
        <h2>Account information</h2>
        <ProfileFieldText
          fieldname='Display Name'
          fieldid='displayName'
          data-testid='displayName'
          value={displayName}
        />
        <ProfilePasswordText data-testid='password'/>
      </div>
    </div>
  );
};

function createBreadCrumbs() {
  const linkDefinitions = [
    { displayName: 'Home', path: '/' },
    { displayName: 'User Profile', path: null },
  ];

  return (
    <div className='breadcrumbs-container'>
      <Breadcrumbs links={linkDefinitions} />
    </div>
  );
}

export default UserProfile;
