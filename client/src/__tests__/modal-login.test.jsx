import React from 'react';
import ReactModal from 'react-modal';
import {
  render, screen, cleanup, fireEvent, getByText, queryByText, findByText
} from '@testing-library/react';

import ModalLogin, { ModalLoginTitle } from '../components/modal-login/modal-login.component';
import { ModalContext } from '../contexts/modal/modal';
import { CurrentUserContext } from '../contexts/current-user/current-user';
import { userApiLogin } from '../paths';
import { act } from 'react-dom/test-utils';

import { setNativeValue, createMockFetch, createErrorJsonData } from '../scripts/test-utilities';

const DEFAULT_USERINFO = {
  email: 'bobby@myforumapp.com',
  password: 'mysecretpassword',
};
const DEFAULT_API_RETURN_INFO = {
  sessionUser: {
      userId: '111',
      userName: 'bobby@myforumapp.com',
      imageUrl: 'http://myforumwebapp.com',
      displayName: 'bobby',
    }
}
const ERRORMSG_INVALID_EMAIL = 'Invalid email';
const ERRORMSG_INVALID_PASSWORD = 'Invalid password';

// setup methods

function createModalWithMocks() {
  const mockLogin = createMockLoginToggle();
  const mockSignup = createMockSignupToggle();
  const mockSetUser = createMockSetUser();
  const response = setupModalLogin(mockLogin, mockSignup, mockSetUser);

  return {
    mocks: { mockLogin, mockSignup, mockSetUser, },
    response
  };
}

function setupModalLogin(mockToggleLogin, mockToggleSignup, mockSetUser) {
  return render(
    <CurrentUserContext.Provider
      value={{
        setCurrentUser: mockSetUser
      }}
    >
      <ModalContext.Provider
        value={{
          isLoginOpen: true,
          toggleLogin: mockToggleLogin,
          toggleSignup: mockToggleSignup,
        }}
      >
        <div id='root'><ModalLogin /></div>
      </ModalContext.Provider>
    </ CurrentUserContext.Provider>
  );
}

function createMockLoginToggle() {
  return jest.fn().mockName('Mocked toggleLogin()');
}

function createMockSignupToggle() {
  return jest.fn().mockName('Mocked toggleSignup()');
}

function createMockSetUser() {
  return jest.fn().mockName('Mocked setCurrentUser()');
}

let originalFetch = null;
beforeEach(() => {
  originalFetch = window.fetch;
});

// cleanup after every test case
afterEach(() => {
  cleanup();
  window.fetch = originalFetch;
});

// suppress warnings
ReactModal.setAppElement('*');

describe('Testing behavior of login modal', () => {
  test('testing that all elements are rendered', () => {
    createModalWithMocks();

    screen.getByTitle(ModalLoginTitle);
    screen.getByAltText('login input email');
    screen.getByAltText('login input password');
    screen.getByTitle('login-button')
    screen.getByTitle('google-login');
    screen.getByTitle('twitter-login');
    screen.getByTitle('link-signup-page');
  });

  test('clicking on the signup button should call toggleLogin and toggleSignup', () => {
    const { mocks: { mockLogin, mockSignup } } = createModalWithMocks();

    screen.getByTitle('link-signup-page').click();

    expect(mockLogin.mock.calls).toHaveLength(1);
    expect(mockSignup.mock.calls).toHaveLength(1);
  });

  test('Login should send values in form to api', async () => {
    createModalWithMocks();
    const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
    window.fetch = mockFetch;

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);

    expect(mockFetch.mock.calls).toHaveLength(1);
    const [ url, options ] = mockFetch.mock.calls[0];
    expect(url).toBe(userApiLogin);
    expect(options).toMatchObject({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify( { userName: email, password } ),
    });
  });

  test('Succesful login should store userinformation in user context', async () => {
    const { mocks: { mockSetUser } } = createModalWithMocks();
    const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
    window.fetch = mockFetch;

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);

    expect(mockSetUser.mock.calls).toHaveLength(1);
    expect(mockSetUser.mock.calls[0][0]).toEqual(DEFAULT_API_RETURN_INFO.sessionUser);
  });

  test('Succesful login should close modal', async () => {
    const { mocks: { mockLogin } } = createModalWithMocks();
    const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
    window.fetch = mockFetch;

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);

    expect(mockLogin.mock.calls).toHaveLength(1);
  });

  test('Malformed email should show validation error notification under input', async () => {
    const emailsToTry = [
      'bobby', 'bobby@', 123, 'bobby@123123', '@foo.com', '', '   ',
    ]

    for (let email of emailsToTry) {
      createModalWithMocks();
      const input = screen.getByAltText('login input email');

      const { password } = DEFAULT_USERINFO;
      await typeInputsAndClickLogin(email, password);

      getByText(input.parentElement, ERRORMSG_INVALID_EMAIL);
      cleanup();
    }
  });


  test('Invalid password should show validation error notification under input', async () => {
    const passwordToTry = [
      '', '         ', '   password   ',
    ]

    for (let password of passwordToTry) {
      createModalWithMocks();
      const input = screen.getByAltText('login input password');

      const { email } = DEFAULT_USERINFO;
      await typeInputsAndClickLogin(email, password);

      getByText(input.parentElement, ERRORMSG_INVALID_PASSWORD);
      cleanup();
    }
  });

  test('Error notification should disappear after succesful validation', async () => {
    const { email, password } = DEFAULT_USERINFO;
    const invalidCredentials = [
      { email: '', password },
      { email, password: '' },
    ]

    for (let credential in invalidCredentials) {
      createModalWithMocks();
      const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
      window.fetch = mockFetch;
      const emailInput = screen.getByAltText('login input email');
      const passwordInput = screen.getByAltText('login input password');

      // make error appear
      await typeInputsAndClickLogin(credential.email, credential.password);
      await typeInputsAndClickLogin(email, password);

      expect( queryByText(emailInput.parentElement, ERRORMSG_INVALID_EMAIL) ).toBeNull();
      expect( queryByText(passwordInput.parentElement, ERRORMSG_INVALID_PASSWORD) ).toBeNull();
      cleanup();
    }
  });

  test('Login failure should show warning under email input', async () => {
    createModalWithMocks();
    const mockFetch = createMockFetch(false, 400, () => 
      Promise.resolve( createErrorJsonData('Invalid email for testing') ) 
    );
    window.fetch = mockFetch;
    const emailInput = screen.getByAltText('login input email');

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);

    await findByText(emailInput.parentElement, 'Invalid email for testing');
  });

  test('Failed password authentication should show warning under password input', async () => {
    createModalWithMocks();
    const mockFetch = createMockFetch(false, 400, () => 
      Promise.resolve( createErrorJsonData('Invalid password for testing') ) 
    );
    window.fetch = mockFetch;
    const passwordInput = screen.getByAltText('login input password');

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);
    
    await findByText(passwordInput.parentElement, 'Invalid password for testing');
  });

  test('Error code 500 should not store information or close modal', async () => {
    const { mocks: { mockSetUser } } = createModalWithMocks();
    window.fetch = createMockFetch(false, 500, () => 
      Promise.resolve( createErrorJsonData('Invalid password for testing') ) 
    );

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);
    
    expect(mockSetUser).toHaveBeenCalledTimes(0);
    screen.getByTitle(ModalLoginTitle);
  });

  test('Error code 500 should not display erorr information', async () => {
    createModalWithMocks();
    window.fetch = createMockFetch(false, 500, () => 
      Promise.resolve( createErrorJsonData('Invalid password for testing') ) 
    );

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);
    
    expect(screen.queryByText('Invalid password for testing')).toBeNull();
  });

  test('Closing dialog should clear input field', async () => {
    createModalWithMocks();
    const emailInput = screen.getByAltText('login input email');
    const passwordInput = screen.getByAltText('login input password');

    const { email, password } = DEFAULT_USERINFO;
    await typeInputs(email, password);
    await closeDialog();

    expect(emailInput.value).toBe('');
    expect(passwordInput.value).toBe('');
  });

  test('Closing dialog should clear error message', async () => {
    createModalWithMocks();
    window.fetch = createMockFetch(false, 400, () => 
      Promise.resolve( createErrorJsonData('Invalid password for testing') )
    );

    const { email, password } = DEFAULT_USERINFO;
    await typeInputsAndClickLogin(email, password);
    await closeDialog();

    expect( screen.queryByText('Invalid password for testing') ).toBeNull();
  });
});

// helper functions

// simulates user interaction with the login form
async function typeInputsAndClickLogin(email, password) {
  await typeInputs(email, password);
  await clickLogin();
}

// simluates user interaction with the inputs
async function typeInputs(email, password) {
  const emailInput = screen.getByAltText('login input email');
  const passwordInput = screen.getByAltText('login input password');

  // when not using react-testing library, need to wrap event emission with act()
  // https://reactjs.org/docs/testing-recipes.html#act
  act(() => {
    const inputEvent = new Event('input', { bubbles: true });
    setNativeValue(emailInput, email);
    fireEvent.input(emailInput, inputEvent);
    setNativeValue(passwordInput, password);
    fireEvent.input(passwordInput, inputEvent);
  });
}

// simluates user clicking on the login button
async function clickLogin() {
  const loginButton = screen.getByTitle('login-button');

    // since stuff inside clickhandler contains async logic, must use async ver of act()
    await act(async () => {
      loginButton.click();
    });
}

// simulates user closing the dialog
async function closeDialog() {
  const login = screen.getByTitle(ModalLoginTitle);
  const escapeKey = new KeyboardEvent('keydown', {
    key: 'Escape', code: 'Escape', charCode: 27, keyCode: 27,
    bubbles: true,
  });

  act(() => {
    fireEvent(login, escapeKey);
  });
}