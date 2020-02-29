import React, { useContext, useState } from 'react';

import { ModalContext } from '../../contexts/modal/modal';
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
  const { isLoginOpen, toggleLogin, toggleSignup } =  useContext(ModalContext);
  const [ email, setEmail ] = useState('');
  const [ password, setPassword ] = useState('');

  const sendLoginInfo = async () => {
    const response = await fetch(userApiLogin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ userName: email, password }),
    });
    
    const { token } = await response.json();
    localStorage.setItem('token', token);
    toggleLogin();
  }

  const loginErrorHandler = () => {

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
          errorMsg={'Invalid username'}
        />
        <FormInput
          id='modal-input-password'
          alt='modal input password'
          type='password'
          placeholder='Password'
          value={password}
          onChange={onPasswordChange}
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