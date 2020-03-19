import React, { useContext, useReducer } from 'react';

import ModalDialog from '../modal-dialog/modal-dialog.component';
import FormInput from '../form-input/form-input.component';
import FormButton from '../form-button/form-button.component';
import Button from '../button/button.component';
import BlockText from '../block-text/block-text.component';

import { ModalContext } from '../../contexts/modal/modal';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { signup } from '../../scripts/api';

import './modal-signup.styles.scss';

export const ModalSignupTitle = 'modal-signup';

const reducer = (state, action) => {
  switch (action.type) {
    case 'setEmail':
      return { ...state, email: action.payload };
    case 'setPassword':
      return { ...state, password: action.payload };
    case 'setConfirmPassword':
      return { ...state, confirmPassword: action.payload };
    case 'setEmailError':
      return { ...state, emailError: action.payload };
    case 'setPasswordError':
      return { ...state, passwordError: action.payload };
    case 'setConfirmPasswordError':
      return { ...state, confirmPasswordError: action.payload };
    default:
      console.log(`unknown action: ${action.type}`);
      return state;
  }
}

const ModalSignup = () => {
  const { toggleSignup, toggleLogin, isSignupOpen } = useContext(ModalContext);
  const { setCurrentUser } = useContext(CurrentUserContext);
  const [ state, dispatch ] = useReducer(reducer, {
    email: '',
    password: '',
    confirmPassword: '',
    emailError: '',
    passwordError: '',
    confirmPasswordError: '',
  });

  const signupHandler = async () => {
    clearErrorMsg();
    if ( !validateInputs() ) return;

    const response = await signup(state.email, state.password);
    if (response.ok)
      await successApiCallHandler(response);
    else
      await failedApiCallHandler(response);
  }
  
  const successApiCallHandler = async (response) => {
    const { sessionUser } = await response.json();
    setCurrentUser(sessionUser);
    onDialogClose();
  }

  const failedApiCallHandler = async (response) => {
    if (response.ignore) return;

    const { error: { description } } = await response.json();
    const includesPassword = (description) => /password/i.test(description);

    if ( includesPassword(description) )
      dispatch({ type: 'setPasswordError', payload: description });
    else
      dispatch({ type: 'setEmailError', payload: description });
  }

  const validateInputs = () => {
    const emailPattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if ( !emailPattern.test(state.email) ) {
      dispatch({ type: 'setEmailError', payload: 'Invalid email' });
      return false;
    }

    const passwordPattern = /^\w+$/;
    if ( !passwordPattern.test(state.password) ) {
      dispatch({ type: 'setPasswordError', payload: 'Invalid password' });
      return false;
    }

    if ( state.password !== state.confirmPassword ) {
      dispatch({ type: 'setConfirmPasswordError', payload: 'Passwords did not match' });
      return false;
    }

    return true;
  }

  const clearInputValue = () => {
    dispatch({ type: 'setEmail', payload: '' });
    dispatch({ type: 'setPassword', payload: '' });
    dispatch({ type: 'setConfirmPassword', payload: '' });
  }

  const clearErrorMsg = () => {
    dispatch({ type: 'setEmailError', payload: '' });
    dispatch({ type: 'setPasswordError', payload: '' });
    dispatch({ type: 'setConfirmPasswordError', payload: '' });
  }

  const onEmailChange = (event) => {
    dispatch({ type: 'setEmail', payload: event.target.value });
  }

  const onPasswordChange = (event) => {
    dispatch({ type: 'setPassword', payload: event.target.value });
  }

  const onConfirmPasswordChange = (event) => {
    dispatch({ type: 'setConfirmPassword', payload: event.target.value });
  }

  const onDialogClose = () => {
    clearInputValue();
    clearErrorMsg();
    toggleSignup();
  }

  const onLoginOpen = () => {
    onDialogClose();
    toggleLogin();
  }

  return (
    <ModalDialog
      className={ModalSignupTitle}
      title={ModalSignupTitle}
      isOpen={isSignupOpen}
      toggleOpen={onDialogClose}
    >
      <h1 className='modal-header'>Signup</h1>
      <div className='modal-content'>
        
        <div className='input-label'>
          <BlockText><label htmlFor='signup-input-email'>Email</label></BlockText>
          <BlockText className='required'>Required</BlockText>
        </div>
        <FormInput
          type='text'
          id='signup-input-email'
          alt='signup input email'
          value={state.email}
          onChange={onEmailChange}
          errorMsg={state.emailError}
        />

        <div className='input-label'>
          <BlockText><label htmlFor='signup-input-password'>Password</label></BlockText>
          <BlockText className='required'>Required</BlockText>
        </div>
        <FormInput
          type='password'
          id='signup-input-password'
          alt='signup input password'
          value={state.password}
          onChange={onPasswordChange}
          errorMsg={state.passwordError}
        />
        
        <div className='input-label'>
          <BlockText><label htmlFor='signup-input-confirm'>Confirm Password</label></BlockText>
          <BlockText className='required'>Required</BlockText>
        </div>
        <FormInput
          type='password'
          id='signup-input-confirm'
          alt='signup input confirm password'
          value={state.confirmPassword}
          onChange={onConfirmPasswordChange}
          errorMsg={state.confirmPasswordError}
        />
        <FormButton
          title='signup button'
          onClick={signupHandler}
        >
          Signup
        </FormButton>
      </div>
      <div className='modal-footer'>
        <BlockText><span>
          Already have an account? Login&nbsp;
          <Button
            title='link login page'
            className='link-login-page'
            onClick={onLoginOpen}
          >
            here
          </Button>
        </span></BlockText>

      </div>

    </ModalDialog>
  );
}

export default ModalSignup;