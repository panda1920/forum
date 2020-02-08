import React, { useContext } from 'react';

import TestEntity from '../testentity/testentity.component';

import UsersContext from '../../contexts/users/users.context';
import { userApi } from '../../paths';

const UserInfo = (props) => {
  const { userId } = props;
  const { fetchUsers } = useContext(UsersContext);
  return (
    <div className='userinfo'>
      <TestEntity
        entity={{ ...props }}
        apiPath={userApi}
        refresh={fetchUsers}
        id={userId}
      />
    </div>
  );
}

export default UserInfo;