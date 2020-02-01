import React, { useState, useContext } from 'react';

import TextInput from '../textinput/textinput.component';

import UsersContext from '../../contexts/users/users.context';
import { changeSignupState, createSubmitHandler } from './signup.logic';
import { userApiCreate } from '../../paths';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [cPassword, setCpassword] = useState('');

  const { fetchUsers } = useContext(UsersContext);
  const submitHandler = createSubmitHandler({
    username, password, cPassword,
    refresh: fetchUsers,
    apiPath: userApiCreate
  });
  
  return (
    <div className='signup'>
      <form id='signup-form' onSubmit={submitHandler}>
        <TextInput
          label='username'
          name='username'
          type='email'
          onChange={ changeSignupState(setUsername) }
        />
        <TextInput
          label='password'
          name='password'
          type='password'
          onChange={ changeSignupState(setPassword) }
        />
        <TextInput
          label='confirm password'
          name='cPassword'
          type='password'
          onChange={ changeSignupState(setCpassword) }
        />
        <button type='submit'>Signup</button>
      </form>
    </div>
  );
}

export default Signup;