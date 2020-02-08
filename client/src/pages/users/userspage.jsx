import React, { useState, useEffect } from 'react';

import UsersContext from '../../contexts/users/users.context';
import Users from '../../components/users/users.component';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    console.log('fetching users!');
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('/userlist');
      const { users } = await response.json();
      setUsers(users);
    }
    catch (error) {
      console.log('Error occured fetching user!', error);
    }
  };
  
  return (
    <div className='users-page'>
      <UsersContext.Provider value={{users, fetchUsers}}>
        <Users />
      </UsersContext.Provider>
    </div>
  );
}

export default UsersPage;