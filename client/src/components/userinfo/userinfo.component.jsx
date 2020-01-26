import React from 'react';

import './userinfo.component.scss';

const UserInfo = (props) => {
  const { userId, userName, displayName, password } = props;
  return (
    <div className='userinfo'>
      <p>userId: {userId}</p>
      <p>userName: {userName}</p>
      <p>displayName: {displayName}</p>
      <p>password: {password}</p>
    </div>
  );
}

export default UserInfo;