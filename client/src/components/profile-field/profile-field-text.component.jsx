import React, { useState, useCallback, useContext }  from 'react';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit } from '@fortawesome/free-solid-svg-icons';

import Button from '../button/button.component';
import BlockText from '../block-text/block-text.component';
import FormInput from '../form-input/form-input.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import useFormInputState from '../../hooks/form-input-state.hooks';

import { updateUser } from '../../scripts/api';

import './profile-field-text.styles.scss';

const ProfileFieldText = (props) => {
  const { value, fieldid, } = props;

  const [ isReadonlyMode, setDisplayMode ] = useState(true);
  const { setCurrentUser, userId } = useContext(CurrentUserContext);
  const formInput = useFormInputState(value);

  // callbacks
  const toggleDisplayMode = useCallback(() => {
    setDisplayMode(previousMode => !previousMode);
    formInput.reset();
  }, [ formInput ]);

  const saveHandler = useCallback(async () => {
    // validate input
    if (!validateInput(formInput.value)) {
      formInput.setError('Invalid input: must not be blank');
      return;
    }
    else
      formInput.setError('');

    // update user
    const response = await updateUser({ userId, [fieldid]: formInput.value });
    const { sessionUser } = await response.json();
    setCurrentUser(sessionUser);

    toggleDisplayMode();
  }, [ setCurrentUser, userId, fieldid, formInput, toggleDisplayMode ]);

  const currentSection = isReadonlyMode ?
    createReadonlySection(props, { toggleDisplayMode, }) :
    createEditSection(props, formInput,
      { saveHandler, toggleDisplayMode, }
    );

  return (
    <div className='profile-field profile-field-text'>
      { currentSection }
    </div>
  );
};

function createReadonlySection(props, callbacks) {
  const { fieldname, value } = props;
  const { toggleDisplayMode } = callbacks;

  return (
    <div className='profile-field-text-section display-mode'>
      <div className='control-section'>
        <BlockText className='label'>{ fieldname }</BlockText>

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
        <BlockText data-testid='display-value'>{ value }</BlockText>
      </div>
    </div>
  );
}

function createEditSection(props, inputState, callbacks) {
  const { fieldname } = props;
  const { saveHandler, toggleDisplayMode, } = callbacks;

  return (
    <div className='profile-field-text-section edit-mode'>
      <div className='control-section'>
        <BlockText className='label'>
          <label htmlFor='profile-field-text-input'>{ fieldname }</label>
        </BlockText>

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
        <FormInput
          id='profile-field-text-input'
          type='text'
          value={inputState.value}
          errorMsg={inputState.error}
          onChange={inputState.onChange}
        />
      </div>
    </div>
  );
}

// helpers
const validateInput = (input) => {
  if (input == null)
    return false;

  const onlyWhitespacePattern = /^\s*$/;
  if ( onlyWhitespacePattern.test(input) )
    return false;
  
  return true;
};

export default ProfileFieldText;
