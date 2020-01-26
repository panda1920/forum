import React, { useState } from 'react';

import Input from '../input/input.component';
import { userApiCreate } from '../../paths';

const Signup = () => {
  // declare states for the input subcomponents
  const [username, setUsername] = useState('');
  const [pw, setPw] = useState('');
  const [cpw, setCpw] = useState('');

  // generate functions to be consumed by each input components
  const generateSetter = (setter) => {
    return (event) => {
      event.preventDefault();
      setter(event.target.value);
    };
  };

  const submitHandler = (event) => {
    event.preventDefault();
    if (! validateInput(username, pw, cpw))
      return;
    
    let formdata = createFormData(username, pw);
    createUser(formdata);
  };
  const validateInput = (username, pw, cpw) => {
    if (pw !== cpw) {
      alert('Password must match');
      return false
    }

    if (!pw || !cpw) {
      alert('Make sure password is not empty');
      return false;
    }

    return true;
  };
  const createFormData = (userName, password) => {
    let formdata = new URLSearchParams();
    formdata.set('userName', userName);
    formdata.set('password', password);
    return formdata;
  };
  const createUser = (body) => {
    let method = 'POST';
    let header = { 'Content-Type': 'application/x-www-form-urlencoded' };
    fetch(userApiCreate, { method, headers: header, body })
    .then(response => {
      if (response.ok) {
        console.log('Success!');
        clearInputs();
      }
      else
        console.log('Failed to create user!');
    })
    .catch(error => {
      console.log(error)
    });
  };
  const clearInputs = () => {
    setUsername('');
    setPw('');
    setCpw('');
  };

  return (
    <div className='signup'>
      <form id='signup-form' onSubmit={submitHandler}>
        <Input
          label='username'
          type='email'
          onChange={ generateSetter(setUsername) }
        />
        <Input
          label='password'
          type='password'
          onChange={ generateSetter(setPw) }
        />
        <Input
          label='confirm password'
          type='password'
          onChange={ generateSetter(setCpw) }
        />
        <button type='submit'>Signup</button>
      </form>
    </div>
  );
}

export default Signup;