import React, { useContext } from 'react';

import { ModalContext } from '../../contexts/modal/modal';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import ModalDialog from '../modal-dialog/modal-dialog.component';
import FormInput from '../form-input/form-input.component';
import FormButton from '../form-button/form-button.component';
import BlockText from '../block-text/block-text.component';
import Button from '../button/button.component';
import useFormInputState from '../../hooks/form-input-state.hooks';

import { ReactComponent as GoogleLogo } from '../../icons/google_signin_buttons/google.svg';
import { ReactComponent as TwitterLogo } from '../../icons/Twitter_Logos/Twitter_Logo_Blue/Twitter_Logo_Blue.svg';

import { login } from '../../scripts/api';

import './modal-login.styles.scss';

export const ModalLoginTitle = 'modal-login';

const ModalLogin = () => {
  const { isLoginOpen, toggleLogin, toggleSignup } = useContext(ModalContext);
  const { setCurrentUser } = useContext(CurrentUserContext);
  const email = useFormInputState('');
  const password = useFormInputState('');

  const sendLoginInfo = async () => {
    if ( !validateInputs() ) return;
    email.setError('');
    password.setError('');

    const response = await login(email.value, password.value);

    if (response.ignore)
      return;
    response.ok ? await loginSuccess(response) : await loginError(response);
  };

  const validateInputs = () => {
    const emailPattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if ( !emailPattern.test(email.value) ) {
      email.setError('Invalid email');
      return false;
    }

    const passwordPattern = /^[^ \t]+$/;
    if ( !passwordPattern.test(password.value) ) {
      password.setError('Invalid password');
      return false;
    }

    return true;
  };

  const loginSuccess = async (response) => {
    const { sessionUser } = await response.json();
    setCurrentUser(sessionUser);
    toggleLogin();
  };

  const loginError = async (response) => {
    const { error: { description } } = await response.json();
    const isPasswordError = /password/i.test(description);

    if (isPasswordError)
      password.setError(description);
    else
      email.setError(description);
  };

  const openSignup = () => {
    closeLogin();
    toggleSignup();
  };

  const closeLogin = () => {
    email.reset();
    password.reset();
    toggleLogin();
  };
  
  return (
    <ModalDialog
      className={ModalLoginTitle}
      title={ModalLoginTitle}
      isOpen={isLoginOpen}
      toggleOpen={closeLogin}
    >
      <h1 className="modal-header">Login</h1>

      <div className='modal-content'>
        <FormInput
          id='login-input-email'
          alt='login input email'
          type='text'
          placeholder='Email'
          value={email.value}
          onChange={email.onChange}
          errorMsg={email.error}
        />
        <FormInput
          id='login-input-password'
          alt='login input password'
          type='password'
          placeholder='Password'
          value={password.value}
          onChange={password.onChange}
          errorMsg={password.error}
        />
        <div className='login-button-section'>
          <FormButton
            title='login-button'
            onClick={sendLoginInfo}
          >
            Login
          </FormButton>
        </div>
        <BlockText className='login-button-or-text'>OR</BlockText>
        <div className='login-thirdparty-button-section'>
          <FormButton title='google-login'>
            <div className='button-with-icons'>
              <GoogleLogo className='button-logo google-logo' />
              <span>Login with Google</span>
            </div>
          </FormButton>
          <FormButton title='twitter-login'>
            <div className='button-with-icons'>
              <TwitterLogo className='button-logo twitter-logo' />
              <span>Login with Twitter</span>
            </div>
          </FormButton>
        </div>
      </div>
      
      <div className='modal-footer'>
        <BlockText><span>
          Don&apos;t have an account? Sign up&nbsp;
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
};

export default ModalLogin;
