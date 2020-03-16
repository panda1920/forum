import React, { useContext, useState } from 'react';

import ModalDialog from '../modal-dialog/modal-dialog.component';
import FormInput from '../form-input/form-input.component';
import FormButton from '../form-button/form-button.component';
import Button from '../button/button.component';
import BlockText from '../block-text/block-text.component';

import { ModalContext } from '../../contexts/modal/modal';
import { signup } from '../../scripts/api';

export const ModalSignupTitle = 'modal-signup';

const ModalSignup = () => {
  const { toggleSignup, isSignupOpen } = useContext(ModalContext);
  const [ email, setEmail ] = useState('');
  const [ password, setPassword ] = useState('');
  const [ confirmPassword, setConfirmPassword ] = useState('');

  const signupHandler = async () => {
    await signup(email, password);
  }

  const onEmailChange = (event) => {
    setEmail(event.target.value);
  }

  const onPasswordChange = (event) => {
    setPassword(event.target.value);
  }

  const onConfirmPasswordChange = (event) => {
    setConfirmPassword(event.target.value);
  }

  return (
    <ModalDialog
      isOpen={isSignupOpen}
      toggleOpen={toggleSignup}
      title={ModalSignupTitle}
    >
      <FormInput
        type='text'
        id='signup-input-email'
        alt='signup input email'
        value={email}
        onChange={onEmailChange}
      />
      <FormInput
        type='password'
        id='signup-input-password'
        alt='signup input password'
        value={password}
        onChange={onPasswordChange}
      />
      <FormInput
        type='password'
        id='signup-input-confirm'
        alt='signup input confirm password'
        value={confirmPassword}
        onChange={onConfirmPasswordChange}
      />
      <FormButton
        title='signup-button'
        onClick={signupHandler}
      >
        Signup
      </FormButton>

      <div className='modal-footer'>
        <BlockText><span>
          Already have an account? Login&nbsp;
          <Button
            title='link-login-page'
            className='link-login-page'
            onClick={() => {}}
          >
            here
          </Button>
        </span></BlockText>

      </div>

    </ModalDialog>
  );
}

export default ModalSignup;