import React, { useContext } from 'react';
import { Redirect } from 'react-router-dom';

import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import ProfileFieldText from '../../components/profile-field-text/profile-field-text.component';
import Spinner from '../../components/spinner/spinner.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './user-profile-page.styles.scss';

// when normal transition, isloggedin returns true
// when direct transition, basepage has not had the change to setcurrentuser
// so regardless of the logged in state isloggedin will be false
// want to make sure that 

const UserProfile = () => {
  const { isLoggedin, beforeFetch } = useContext(CurrentUserContext);

  if (beforeFetch)
    return <Spinner />;
  if (!isLoggedin())
    return <Redirect to='/' />;

  return (
    <div className='user-profile-page'>
      { createBreadCrumbs() }
      <div className='user-profile-page-info'>
        <h1>User info</h1>
      </div>
      <ProfileFieldText fieldname='hello' value='test_field'/>
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
