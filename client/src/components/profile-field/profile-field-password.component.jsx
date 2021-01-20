import React, { useState, useCallback, useContext }  from 'react';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit } from '@fortawesome/free-solid-svg-icons';

import Button from '../button/button.component';
import BlockText from '../block-text/block-text.component';
import FormInput from '../form-input/form-input.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import useFormInputState from '../../hooks/form-input-state.hooks';

import { updateUser, verifyCredentials } from '../../scripts/api';

import './profile-field-password.styles.scss';

const ProfileFieldText = () => {
  const [ isReadonlyMode, setDisplayMode ] = useState(true);
  const oldPassword = useFormInputState('');
  const newPassword = useFormInputState('');
  const confPassword = useFormInputState('');

  const { setCurrentUser, userId } = useContext(CurrentUserContext);

  // callbacks
  const toggleDisplayMode = useCallback(() => {
    setDisplayMode(previousMode => !previousMode);
    oldPassword.reset();
    newPassword.reset();
    confPassword.reset();
  }, [ oldPassword, newPassword, confPassword ]);

  const saveHandler = useCallback(async () => {
    // reset all errors
    oldPassword.setError('');
    newPassword.setError('');
    confPassword.setError('');

    // validate all inputs
    let hasNoError = validateState(oldPassword)
    hasNoError = validateState(newPassword) && hasNoError;
    hasNoError = validateState(confPassword) && hasNoError;
    if (newPassword.value !== confPassword.value) {
      newPassword.setError('Invalid value: password must match');
      confPassword.setError('Invalid value: password must match');
      hasNoError = false;
    }

    if (!hasNoError) return;

    // verify credentials before update
    let response = await verifyCredentials({ password: oldPassword.value });
    if (!response.ok) {
      oldPassword.setError('Invalid value: verification failed');
      return;
    }

    // update user info
    response = await updateUser({ userId, password: newPassword.value });
    const { sessionUser } = await response.json();
    setCurrentUser(sessionUser);
  }, [ setCurrentUser, userId, oldPassword, newPassword, confPassword ]);

  const currentSection = isReadonlyMode ?
    createReadonlySection({ toggleDisplayMode }) :
    createEditSection(
      { oldPassword, newPassword, confPassword },
      { saveHandler, toggleDisplayMode }
    );

  return (
    <div className='profile-field profile-field-password'>
      { currentSection }
    </div>
  );
};

function createReadonlySection(callbacks) {
  const { toggleDisplayMode } = callbacks;

  return (
    <div className='profile-field-password-section display-mode'>
      <div className='control-section'>
        <BlockText className='label'>Password</BlockText>

        <div className='buttons'>
          <Button
            className='icon-button'
            data-testid='edit-button'
            onClick={toggleDisplayMode}
            key='edit-button'
          >
            <FontAwesomeIcon icon={faEdit} />
          </Button>
        </div>
      </div>

      <div className='fieldvalue-section'>
        <BlockText data-testid='display-value'>********</BlockText>
      </div>
    </div>
  );
}

function createEditSection(inputStates, callbacks) {
  const { oldPassword, newPassword, confPassword } = inputStates;
  const { saveHandler, toggleDisplayMode } = callbacks;

  return (
    <div className='profile-field-password-section edit-mode'>
      <div className='control-section'>
        <BlockText className='label'>Password</BlockText>

        <div className='buttons'>
          <Button
            className='text-button'
            data-testid='save-button'
            onClick={saveHandler}
            key='save-button'
          >
            Save
          </Button>
          <Button
            className='text-button'
            data-testid='cancel-button'
            onClick={toggleDisplayMode}
            key='cancel-button'
          >
            Cancel
          </Button>
        </div>
      </div>

      <div className='fieldvalue-section'>
        <BlockText className='label'>
          <label htmlFor='profile-field-old-input'>Old Password</label>
        </BlockText>
        <FormInput
          id='profile-field-old-input'
          type='password'
          value={oldPassword.value}
          errorMsg={oldPassword.error}
          onChange={oldPassword.onChange}
        />

        <BlockText className='label'>
          <label htmlFor='profile-field-new-input'>New Password</label>
        </BlockText>
        <FormInput
          id='profile-field-new-input'
          type='password'
          value={newPassword.value}
          errorMsg={newPassword.error}
          onChange={newPassword.onChange}
        />

        <BlockText className='label'>
          <label htmlFor='profile-field-confirm-input'>Confirm Password</label>
        </BlockText>
        <FormInput
          id='profile-field-confirm-input'
          type='password'
          value={confPassword.value}
          errorMsg={confPassword.error}
          onChange={confPassword.onChange}
        />
      </div>
    </div>
  );
}

// helpers
const validateInput = (input) => {
  if (input == null)
    throw Error('Invalid input: must not be blank.');

  const onlyWhitespacePattern = /^\s*$/;
  if ( onlyWhitespacePattern.test(input) )
    throw Error('Invalid input: must not be blank or only whitespaces.');

  if (input.length < 6) {
    throw Error('Invalid input: password must be atleast 6 characters long.');
  }
};

const validateState = (inputState) => {
  try {
    validateInput(inputState.value);
    return true;
  }
  catch(e) {
    inputState.setError(e.message);
    return false;
  }
};

export default ProfileFieldText;
