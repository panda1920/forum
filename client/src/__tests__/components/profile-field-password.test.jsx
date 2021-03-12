import React from 'react';
import { render, screen, act, cleanup, getByText } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ProfileFieldPassword from '../../components/profile-field/profile-field-password.component';

import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { updateUser, verifyCredentials } from '../../scripts/api';
import { createMockFetchImplementation } from '../../scripts/test-utilities';

// mock functions
jest.mock('../../scripts/api', () => ({
  updateUser: jest.fn().mockName('mocked updateUser()'),
  verifyCredentials: jest.fn().mockName('mocked verifyCredentials()'),
}));

const TEST_DATA = {
  CURRENT_USER: {
    userId: 'test_userid',
  },
  API_RETURN: {
    sessionUser: {
      userId: 'test_sessionuserid',
    },
  },
  DEFAULT_PASSWORD: 'password',
};

const IDENTIFIERS = {
  EDIT_BUTTON_ID: 'edit-button',
  SAVE_BUTTON_ID: 'save-button',
  CANCEL_BUTTON_ID: 'cancel-button',
  DISPLAY_VALUE_ID: 'display-value',
  DISPLAY_FIELDNAME: 'Password',
  OLD_PASSWORD_LABEL: 'Old Password',
  NEW_PASSWORD_LABEL: 'New Password',
  CONFIRM_PASSWORD_LABEL: 'Confirm Password',
};


function renderProfileFieldText() {
  const mockSetCurrentUser = jest.fn().mockName('mocked setCurrentUser()');

  const renderResult = render(
    <CurrentUserContext.Provider
      value={{ ...TEST_DATA.CURRENT_USER, setCurrentUser: mockSetCurrentUser }}
    >
      <ProfileFieldPassword/>
    </CurrentUserContext.Provider>
  );

  return {
    ...renderResult,
    mocks: { mockSetCurrentUser },
  };
}

beforeEach(() => {
  jest.useFakeTimers();
  updateUser.mockImplementation(
    createMockFetchImplementation(true, 200, async () => TEST_DATA.API_RETURN)
  );
  verifyCredentials.mockImplementation(
    createMockFetchImplementation(true, 200, async () => {})
  );
});
afterEach(() => {
  cleanup();
  updateUser.mockClear();
  verifyCredentials.mockClear();
  jest.useRealTimers();
});

describe('Testing that subcomponents are rendered', () => {
  test('Field name and value are rendered', () => {
    renderProfileFieldText();

    expect( screen.getByText(IDENTIFIERS.DISPLAY_FIELDNAME) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.DISPLAY_VALUE_ID) )
      .toBeInTheDocument();
  });

  test('Password field should display asterisks', () => {
    renderProfileFieldText();

    const password_value = screen.getByTestId(IDENTIFIERS.DISPLAY_VALUE_ID);

    expect( getByText(password_value, /^\**$/) ).toBeInTheDocument();
  });

  test('Edit button is rendered', () => {
    renderProfileFieldText();

    expect( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Input field, save/cancel button is not rendered initially', () => {
    renderProfileFieldText();

    expect( screen.queryByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .not.toBeInTheDocument();
  });
});

describe('Testing behavior of ProfileFieldText', () => {
  test('Input field, save/cancel button is rendered when edit button is pressed', () => {
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.queryByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL) )
      .toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL) )
      .toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Input field that appears when edit button is pressed should not be prepopulated with value', () => {
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.queryByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL) )
      .toHaveValue('');
    expect( screen.queryByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL) )
      .toHaveValue('');
    expect( screen.queryByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL) )
      .toHaveValue('');
  });

  test('value display and edit button is not rendered when edit button is pressed', () => {
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.queryByTestId(IDENTIFIERS.DISPLAY_VALUE_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .not.toBeInTheDocument();
  });

  test('Clicking on save button with invalid old password should trigger error', async () => {
    const invalidValues = [' ', '　', '\t', '12345'];
    const validValue = TEST_DATA.DEFAULT_PASSWORD;

    for (const invalidValue of invalidValues) {
      renderProfileFieldText();
  
      // switch to edit mode
      userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

      // type in some value and click save
      const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
      const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
      const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
      const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
      userEvent.type(oldPasswordInput, invalidValue);
      userEvent.type(newPasswordInput, validValue);
      userEvent.type(confPasswordInput, validValue);
      await act(async () => userEvent.click(saveButton));

      expect(screen.getByText(/invalid/i)).toBeInTheDocument();

      cleanup();
    }
  });

  test('Clicking on save button with nonmatching new and confirm should trigger error', async () => {
    const validValue = TEST_DATA.DEFAULT_PASSWORD;

    renderProfileFieldText();
  
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validValue);
    userEvent.type(newPasswordInput, 'password1');
    userEvent.type(confPasswordInput, 'password2');
    await act(async () => userEvent.click(saveButton));

    expect(screen.getAllByText(/invalid/i)).toHaveLength(2);
  });

  test('Clicking on save button with matching but invalid new and confirm should trigger error', async () => {
    const invalidValues = [' ', '　', '\t', '12345'];
    const validValue = TEST_DATA.DEFAULT_PASSWORD;

    for (const invalidValue of invalidValues) {
      renderProfileFieldText();
  
      // switch to edit mode
      userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );
  
      // type in some value and click save
      const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
      const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
      const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
      const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
      userEvent.type(oldPasswordInput, validValue);
      userEvent.type(newPasswordInput, invalidValue);
      userEvent.type(confPasswordInput, invalidValue);
      await act(async () => userEvent.click(saveButton));
  
      expect(screen.getAllByText(/invalid/i)).toHaveLength(2);
  
      cleanup();
    }
  });

  test('Clicking on save button with valid values should trigger confirmCredential API', async  () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';
    const expectedCredentials = {
      userId: TEST_DATA.CURRENT_USER.userId,
      password: validOldPassword
    };

    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validOldPassword);
    userEvent.type(newPasswordInput, validNewpassword);
    userEvent.type(confPasswordInput, validNewpassword);
    await act(async () => userEvent.click(saveButton));

    expect(verifyCredentials).toHaveBeenCalledTimes(1);
    const [ credentials ] = verifyCredentials.mock.calls[0];
    expect(credentials).toMatchObject(expectedCredentials);
  });

  test('Clicking on save button with valid values should trigger update API call', async () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';
    const expectedUpdate = {
      userId: TEST_DATA.CURRENT_USER.userId,
      password: validNewpassword,
    };
    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validOldPassword);
    userEvent.type(newPasswordInput, validNewpassword);
    userEvent.type(confPasswordInput, validNewpassword);
    await act(async () => userEvent.click(saveButton));

    expect(updateUser).toHaveBeenCalledTimes(1);
    const [ update ] = updateUser.mock.calls[0];
    expect(update).toMatchObject(expectedUpdate);
  });

  test('Clicking on save button should reload user data from API returned value', async () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';
    const { mocks: { mockSetCurrentUser } } = renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validOldPassword);
    userEvent.type(newPasswordInput, validNewpassword);
    userEvent.type(confPasswordInput, validNewpassword);
    await act(async () => userEvent.click(saveButton));

    expect(mockSetCurrentUser).toHaveBeenCalledTimes(1);
    const [ sessionUser ] = mockSetCurrentUser.mock.calls[0];
    expect(sessionUser).toMatchObject(TEST_DATA.API_RETURN.sessionUser);
  });

  test('Clicking on save button with valid values should switch back from edit mode', async () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';
    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validOldPassword);
    userEvent.type(newPasswordInput, validNewpassword);
    userEvent.type(confPasswordInput, validNewpassword);
    await act(async () => userEvent.click(saveButton));

    expect( screen.queryByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .not.toBeInTheDocument();

    expect( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Clicking on save button with invalid values should not send API call', async () => {
    const validPassword = TEST_DATA.DEFAULT_PASSWORD;
    const invalidPassword = ' ';
    const invalidValueCombinations = [
      [ invalidPassword, validPassword, validPassword ],
      [ validPassword, invalidPassword, invalidPassword ],
      [ validPassword, validPassword + '_new', validPassword ],
    ];

    for (const invalidValues of invalidValueCombinations) {
      const { mocks: { mockSetCurrentUser } } = renderProfileFieldText();
    
      // switch to edit mode
      userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );
  
      // type in some value and click save
      const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
      const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
      const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
      const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
      userEvent.type(oldPasswordInput, invalidValues[0]);
      userEvent.type(newPasswordInput, invalidValues[1]);
      userEvent.type(confPasswordInput, invalidValues[2]);
      await act(async () => userEvent.click(saveButton));

      expect(verifyCredentials).not.toHaveBeenCalled();
      expect(updateUser).not.toHaveBeenCalled();
      expect(mockSetCurrentUser).not.toHaveBeenCalled();

      cleanup();
    }
  });

  test('When old password confirmation fails during save, error is displayed', async () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';
    verifyCredentials.mockImplementation(
      createMockFetchImplementation(false, 400, async () => {})
    );
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validOldPassword);
    userEvent.type(newPasswordInput, validNewpassword);
    userEvent.type(confPasswordInput, validNewpassword);
    await act(async () => userEvent.click(saveButton));

    expect( screen.queryByText( /invalid/i ) ).toBeInTheDocument();
  });

  test('When old password confirmation fails during save, update API is not called', async () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';
    verifyCredentials.mockImplementation(
      createMockFetchImplementation(false, 400, async () => {})
    );
    const { mocks: { mockSetCurrentUser } } = renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // type in some value and click save
    const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
    const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
    const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    userEvent.type(oldPasswordInput, validOldPassword);
    userEvent.type(newPasswordInput, validNewpassword);
    userEvent.type(confPasswordInput, validNewpassword);
    await act(async () => userEvent.click(saveButton));

    expect(updateUser).not.toHaveBeenCalled();
    expect(mockSetCurrentUser).not.toHaveBeenCalled();
  });

  test('Clicking on save button with valid input when error is displayed should clear error', async () => {
    const validPassword = TEST_DATA.DEFAULT_PASSWORD;
    const validNewPassword = validPassword + '_new';
    const invalidPassword = ' ';
    const invalidValueCombinations = [
      [ invalidPassword, validPassword, validPassword ],
      [ validPassword, invalidPassword, invalidPassword ],
      [ validPassword, validPassword + '_new', validPassword ],
    ];

    for (const invalidValues of invalidValueCombinations) {
      renderProfileFieldText();
      
      // switch to edit mode
      userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );
  
      const oldPasswordInput = screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL);
      const newPasswordInput = screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL);
      const confPasswordInput = screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL);
      const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
      
      // display error
      userEvent.type(oldPasswordInput, invalidValues[0]);
      userEvent.type(newPasswordInput, invalidValues[1]);
      userEvent.type(confPasswordInput, invalidValues[2]);
      await act(async () => userEvent.click(saveButton));
      jest.runAllTimers(); // go around double submission prevention

      userEvent.clear(oldPasswordInput);
      userEvent.clear(newPasswordInput);
      userEvent.clear(confPasswordInput);

      // save with valid value
      userEvent.type(oldPasswordInput, validPassword);
      userEvent.type(newPasswordInput, validNewPassword);
      userEvent.type(confPasswordInput, validNewPassword);
      await act(async () => userEvent.click(saveButton));
  
      expect( screen.queryByText( /invalid/i ) ).not.toBeInTheDocument();
      
      cleanup();
    }
  });

  test('Clicking on cancel button should cause input field and ok/cancel button to disappear', () => {
    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // switch to readonly
    userEvent.click( screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) );

    expect( screen.queryByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .not.toBeInTheDocument();
  });

  test('Clicking on cancel button should cause field value and edit button to reappear', () => {
    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // switch to readonly
    userEvent.click( screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) );

    const passwordValue = screen.getByTestId(IDENTIFIERS.DISPLAY_VALUE_ID);
    expect( getByText(passwordValue, /^\**$/) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Clicking on cancel should repopulate the original value in input', () => {
    const validOldPassword = TEST_DATA.DEFAULT_PASSWORD + '_old';
    const validNewpassword = TEST_DATA.DEFAULT_PASSWORD + '_new';

    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // put some input and exit edit mode
    userEvent.type(
      screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL), validOldPassword
    );
    userEvent.type(
      screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL), validNewpassword
    );
    userEvent.type(
      screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL), validNewpassword
    );
    userEvent.click( screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) );

    // switch to edit mode again
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL) )
      .toHaveValue('');
    expect( screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL) )
      .toHaveValue('');
    expect( screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL) )
      .toHaveValue('');
  });

  test('Clicking on cancel should clear errros', async () => {
    const validPassword = TEST_DATA.DEFAULT_PASSWORD;
    const invalidPassword = ' ';
    const invalidValueCombinations = [
      [ invalidPassword, validPassword, validPassword ],
      [ validPassword, invalidPassword, invalidPassword ],
      [ validPassword, validPassword + '_new', validPassword ],
    ];

    for (const invalidValues of invalidValueCombinations) {
      renderProfileFieldText();
  
      // switch to edit mode
      userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );
  
      // put some input, show error and exit edit mode
      userEvent.type(
        screen.getByLabelText(IDENTIFIERS.OLD_PASSWORD_LABEL), invalidValues[0]
      );
      userEvent.type(
        screen.getByLabelText(IDENTIFIERS.NEW_PASSWORD_LABEL), invalidValues[1]
      );
      userEvent.type(
        screen.getByLabelText(IDENTIFIERS.CONFIRM_PASSWORD_LABEL), invalidValues[2]
      );
      const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID)
      await act(async () => userEvent.click(saveButton) );
      userEvent.click( screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) );

      // switch to edit mode again
      userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );
  
      expect( screen.queryByText(/invalid/i) )
        .not.toBeInTheDocument();

      cleanup();
    }
  });
});
