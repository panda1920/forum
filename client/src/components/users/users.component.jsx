import React, { useContext } from 'react';

import UsersContext from '../../contexts/users/users.context';
import UserInfo from  '../userinfo/userinfo.component';
import Signup from '../signup/signup.component';

const Users = () => {
  const { users } = useContext(UsersContext);
  
  return (
    <div className='users'>
      {
        users.map(user => {
          return <UserInfo key={user.userId} {...user} />
        })
      }
      <Signup />
    </div>
  );
}

export default Users;