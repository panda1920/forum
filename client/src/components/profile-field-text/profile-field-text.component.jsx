import React, { useState, useCallback, useContext }  from 'react';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit } from '@fortawesome/free-solid-svg-icons';

import Button from '../button/button.component';
import BlockText from '../block-text/block-text.component';
import FormInput from '../form-input/form-input.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import { updateUser } from '../../scripts/api';

import './profile-field-text.styles.scss';

const ProfileFieldText = (props) => {
  const { value, fieldid, } = props;

  const [ isReadonlyMode, setDisplayMode ] = useState(true);
  const [ error, setError ] = useState('');
  const [ input, setInput ] = useState(value);

  const { setCurrentUser, userId } = useContext(CurrentUserContext);

  // callbacks
  const toggleDisplayMode = useCallback(() => {
    setDisplayMode(previousMode => !previousMode);
    setInput(value);
    setError('');
  }, [ value ]);

  const validateInput = useCallback((input) => {
    if (input == null)
      return false;

    const onlyWhitespacePattern = /^\s*$/;
    if ( onlyWhitespacePattern.test(input) )
      return false;
    
    return true;
  }, []);

  const saveHandler = useCallback(async () => {
    if (!validateInput(input)) {
      setError('Invalid input: must not be blank');
      return;
    }
    else
      setError('');

    const response = await updateUser({ userId, [fieldid]: input });
    const { sessionUser } = await response.json();

    setCurrentUser(sessionUser);
  }, [ setCurrentUser, validateInput, userId, fieldid, input ]);

  const onChangeHandler = (e) => {
    setInput(e.target.value);
  };

  const currentSection = isReadonlyMode ?
    createReadonlySection(props, { toggleDisplayMode, }) :
    createEditSection(props, input, error,
      { saveHandler, toggleDisplayMode, onChangeHandler }
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

function createEditSection(props, input, error, callbacks) {
  const { fieldname } = props;
  const { saveHandler, toggleDisplayMode, onChangeHandler } = callbacks;

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
          value={input}
          errorMsg={error}
          onChange={onChangeHandler}
        />
      </div>
    </div>
  );
}

export default ProfileFieldText;
