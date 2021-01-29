import React from 'react';
import { render, screen, act, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ProfileFieldText from '../../components/profile-field/profile-field-text.component';

import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { updateUser } from '../../scripts/api';
import { createMockFetchImplementation } from '../../scripts/test-utilities';

// mock functions
jest.mock('../../scripts/api', () => ({
  updateUser: jest.fn().mockName('mocked updateUser()'),
}));

const TEST_DATA = {
  DEFAULT_FIELDNAME: 'test_field', // used for displaying
  DEFAULT_FIELDID: 'test_fieldid', // used for api call
  DEFAULT_FIELDVALUE: 'test_value',
  CURRENT_USER: {
    userId: 'test_userid',
  },
  API_RETURN: {
    sessionUser: {
      userId: 'test_sessionuserid',
    },
  },
};

const IDENTIFIERS = {
  EDIT_BUTTON_ID: 'edit-button',
  SAVE_BUTTON_ID: 'save-button',
  CANCEL_BUTTON_ID: 'cancel-button',
  DISPLAY_VALUE_ID: 'display-value',
};


function renderProfileFieldText() {
  const mockSetCurrentUser = jest.fn().mockName('mocked setCurrentUser()');

  const renderResult = render(
    <CurrentUserContext.Provider
      value={{ ...TEST_DATA.CURRENT_USER, setCurrentUser: mockSetCurrentUser }}
    >
      <ProfileFieldText
        fieldname={ TEST_DATA.DEFAULT_FIELDNAME }
        fieldid={ TEST_DATA.DEFAULT_FIELDID }
        value={ TEST_DATA.DEFAULT_FIELDVALUE }
      />
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
});
afterEach(() => {
  cleanup();
  updateUser.mockClear();
  jest.useRealTimers();
});

describe('Testing that subcomponents are rendered', () => {
  test('Field name and value are rendered', () => {
    renderProfileFieldText();

    expect( screen.getByText(TEST_DATA.DEFAULT_FIELDNAME) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.DISPLAY_VALUE_ID) )
      .toBeInTheDocument();
  });

  test('Edit button is rendered', () => {
    renderProfileFieldText();

    expect( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Input field, save/cancel button is not rendered initially', () => {
    renderProfileFieldText();

    expect( screen.queryByLabelText(TEST_DATA.DEFAULT_FIELDNAME) )
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

    expect( screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Input field that appears when edit button is pressed should be prepopulated with value', () => {
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME) )
      .toHaveValue(TEST_DATA.DEFAULT_FIELDVALUE);
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

  test('Pressing on save button should trigger update API call', async () => {
    const expectedUpdate = {
      userId: TEST_DATA.CURRENT_USER.userId,
      [TEST_DATA.DEFAULT_FIELDID]: TEST_DATA.DEFAULT_FIELDVALUE,
    };
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);

    await act( async () => userEvent.click(saveButton) );

    expect(updateUser).toHaveBeenCalledTimes(1);
    const [ updateArg ] = updateUser.mock.calls[0];
    expect(updateArg).toMatchObject(expectedUpdate);
  });

  test('Pressing on save button should reload user data from API returned value', async () => {
    const { mocks: { mockSetCurrentUser } } = renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);

    // need to wrap in await act because click tiggers several async tasks
    await act(async () => userEvent.click(saveButton) );

    expect(mockSetCurrentUser).toHaveBeenCalledTimes(1);
    const [ sessionUser ] = mockSetCurrentUser.mock.calls[0];
    expect(sessionUser).toMatchObject(TEST_DATA.API_RETURN.sessionUser);
  });

  test('Pressing on save button with invalid input value should display error', async () => {
    const invalidValues = ['', ' ', '　', '\t'];

    for (const invalidValue of invalidValues) {
      renderProfileFieldText();
    
      // switch to edit mode
      const editButton = screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID);
      userEvent.click(editButton);

      const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
      const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);
  
      // due to a bug? where userEvent doesn't allow empty space typing
      // https://github.com/testing-library/user-event/issues/182
      if (invalidValue === '') {
        // userEvent.clear(input); // .clear() is not implemented in this ver
        cleanup();
        continue;
      }
      else
        userEvent.type(input, invalidValue);
      await act(async () => userEvent.click(saveButton) );

      expect(input).toHaveValue(invalidValue);
      expect( screen.getByText( /invalid/i ) ).toBeInTheDocument();

      cleanup();
    }
  });

  test('Pressing on save button with invalid input should not send API call', async () => {
    const invalidValue = ' ';
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);

    userEvent.type(input, invalidValue);
    await act(async () => userEvent.click(saveButton) );

    expect(updateUser).not.toHaveBeenCalled();
  });

  test('Pressing on save button with valid input when error is displayed should clear error', async () => {
    const invalidValue = ' ';
    const validValue = 'hello world';
    renderProfileFieldText();
    
    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);
    
    // display error
    userEvent.type(input, invalidValue);
    await act(async () => userEvent.click(saveButton) );
    jest.runAllTimers(); // need this because Button uses settimer to prevent rapid click

    // click save with valid value
    userEvent.type(input, validValue);
    await act(async () => userEvent.click(saveButton));

    expect( screen.queryByText( /invalid/i ) ).not.toBeInTheDocument();
  });

  test('Clicking on save button with valid values should switch back from edit mode', async () => {
    const validValue = 'hello world';

    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // input and save
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);
    userEvent.type(input, validValue);
    await act(async () => userEvent.click(saveButton) );

    expect( screen.queryByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByLabelText(TEST_DATA.DEFAULT_FIELDNAME) )
      .not.toBeInTheDocument();
    
    expect( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Pressing on cancel button should cause input field and ok/cancel button to disappear', () => {
    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    const cancelButton = screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID);

    userEvent.click(cancelButton);

    expect( screen.queryByLabelText(TEST_DATA.DEFAULT_FIELDNAME) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.SAVE_BUTTON_ID) )
      .not.toBeInTheDocument();
    expect( screen.queryByTestId(IDENTIFIERS.CANCEL_BUTTON_ID) )
      .not.toBeInTheDocument();
  });

  test('Pressing on cancel button should cause field value and edit button to reappear', () => {
    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    const cancelButton = screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID);
    userEvent.click(cancelButton);

    expect( screen.getByTestId(IDENTIFIERS.DISPLAY_VALUE_ID) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) )
      .toBeInTheDocument();
  });

  test('Pressing on cancel button after change in input value should not affect value', () => {
    const inputs = [
      '',
      ' ',
      'hello world',
      'a',
    ];

    for (const inputValue of inputs) {
      renderProfileFieldText();

      // switch to edit mode
      const editButton = screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID);
      userEvent.click(editButton);
  
      const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);
      userEvent.type(input, inputValue);
      
      const cancelButton = screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID);
      userEvent.click(cancelButton);

      expect( screen.getByText(TEST_DATA.DEFAULT_FIELDVALUE) )
        .toBeInTheDocument();

      cleanup();
    }
  });

  test('Pressing on cancel should repopulate the original value in input', () => {
    const inputValue = ' ';

    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // put some input and exit edit mode
    const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);
    userEvent.type(input, inputValue);
    const cancelButton = screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID);
    userEvent.click(cancelButton);

    // switch to edit mode again
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME) )
      .toHaveValue(TEST_DATA.DEFAULT_FIELDVALUE);
  });

  test('Pressing on cancel should clear errros', async () => {
    const invalidValue = ' ';

    renderProfileFieldText();

    // switch to edit mode
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    // put some input, show error and exit edit mode
    const input = screen.getByLabelText(TEST_DATA.DEFAULT_FIELDNAME);
    const saveButton = screen.getByTestId(IDENTIFIERS.SAVE_BUTTON_ID);
    const cancelButton = screen.getByTestId(IDENTIFIERS.CANCEL_BUTTON_ID);
    userEvent.type(input, invalidValue);
    await act(async () => userEvent.click(saveButton) );
    userEvent.click(cancelButton);

    // switch to edit mode again
    userEvent.click( screen.getByTestId(IDENTIFIERS.EDIT_BUTTON_ID) );

    expect( screen.queryByText(/invalid/i) )
      .not.toBeInTheDocument();
  });
});
