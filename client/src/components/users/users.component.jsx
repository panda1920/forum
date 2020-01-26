import React, { useState, useEffect } from 'react';

import UserInfo from  '../userinfo/userinfo.component';

const Users = () => {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    console.log('fetching users!');

    fetch('/userlist')
    .then(response => {
      return response.json();
    })
    .then(json => {
      const { users } = json;
      setUsers(users);
    })
    .catch(error => {
      console.log('Error occured!');
      console.log(error);
    });
  }, []);
  
  return (
    <div className='users'>
      {
        users.map(user => {
          return <UserInfo key={user.userId} {...user} />
        })
      }
    </div>
  );
}

export default Users;