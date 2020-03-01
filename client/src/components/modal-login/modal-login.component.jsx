import React, { useContext, useState } from 'react';

import { ModalContext } from '../../contexts/modal/modal';
import { CurrentUserContext } from '../../contexts/currentUser/currentUser';
import ModalDialog from '../modal-dialog/modal-dialog.component';
import FormInput from '../form-input/form-input.component';
import FormButton from '../form-button/form-button.component';
import BlockText from '../block-text/block-text.component';
import Button from '../button/button.component';
import { ReactComponent as GoogleLogo } from '../../icons/google_signin_buttons/web/vector/btn_google_light_normal_ios.svg';
import { ReactComponent as TwitterLogo } from '../../icons/Twitter_Logos/Twitter_Logo_Blue/Twitter_Logo_Blue.svg';

import { userApiLogin } from '../../paths';

import './modal-login.styles.scss';

export const ModalLoginTitle = 'modal-login';

const ModalLogin = () => {
  const { isLoginOpen, toggleLogin, toggleSignup } = useContext(ModalContext);
  const { setCurrentUser } = useContext(CurrentUserContext);
  const [ email, setEmail ] = useState('');
  const [ password, setPassword ] = useState('');
  const [ emailError, setEmailError ] = useState('');
  const [ passwordError, setPasswordError ] = useState('');

  const sendLoginInfo = async () => {
    if (! validateInputs()) return;
    resetInputs();
    
    const response = await fetch(userApiLogin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ userName: email, password }),
    });
    
    if (!response.ok) {
      loginErrorHandler(response);
      return;
    }
    else {
      const { users } = await response.json();
      setCurrentUser(users[0]);
      toggleLogin();
    }
  }

  const validateInputs = () => {
    const emailPattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if ( !emailPattern.test(email) ) {
      setEmailError('Invalid email');
      return false;
    }

    const passwordPattern = /^[^ \t]+$/;
    if ( !passwordPattern.test(password) ) {
      setPasswordError('Invalid password');
      return false;
    }

    return true;
  }

  const resetInputs = () => {
    setEmailError('');
    setPasswordError('');
  }

  const loginErrorHandler = async (response) => {
    const { error: { description } } = await response.json();
    const isPasswordError = /password/i.test(description);

    if (isPasswordError)
      setPasswordError(description);
    else
      setEmailError(description);
  };

  const onEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const onPasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const openSignup = () => {
    toggleLogin();
    toggleSignup();
  };
  
  return (
    <ModalDialog
      isOpen={isLoginOpen}
      toggleOpen={toggleLogin}
      title={ModalLoginTitle}
    >
      <h1 className="modal-header">Login</h1>

      <div className='modal-content'>
        <FormInput
          id='modal-input-email'
          alt='modal input email'
          type='text'
          placeholder='Email'
          value={email}
          onChange={onEmailChange}
          errorMsg={emailError}
        />
        <FormInput
          id='modal-input-password'
          alt='modal input password'
          type='password'
          placeholder='Password'
          value={password}
          onChange={onPasswordChange}
          errorMsg={passwordError}
        />
        <div className='login-button-section'>
          <FormButton
            title='login-button'
            onClick={sendLoginInfo}
          >
            Login
          </FormButton>
        </div>
        <BlockText>OR</BlockText>
        <div className='login-thirdparty-button-section'>
          <FormButton title='google-login'>
            <div className='button-with-icons'>
              <GoogleLogo className='button-logo' />
              <span>Login with Google</span>
            </div>
          </FormButton>
          <FormButton title='twitter-login'>
            <div className='button-with-icons'>
              <TwitterLogo className='button-logo' />
              <span>Login with Twitter</span>
            </div>
          </FormButton>
        </div>
      </div>
      
      <div className='modal-footer'>
        <BlockText><span>
          Don't have an account? Sign up&nbsp;
          <Button
            title='link-signup-page'
            className='link-signup-page'
            onClick={openSignup}
          >
            here
          </Button>
        </span></BlockText>
      </div>
    </ModalDialog>
  );
}

export default ModalLogin;