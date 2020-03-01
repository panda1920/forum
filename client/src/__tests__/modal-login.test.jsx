import React, { useState } from 'react';
import ReactModal from 'react-modal';
import {
  render, screen, cleanup, fireEvent, getByText, queryByText, findByText
} from '@testing-library/react';

import ModalLogin, { ModalLoginTitle } from '../components/modal-login/modal-login.component';
import { ModalContext } from '../contexts/modal/modal';
import { CurrentUserContext } from '../contexts/currentUser/currentUser';
import { userApiLogin } from '../paths';

const DEFAULT_USERINFO = {
  email: 'bobby@myforumapp.com',
  password: 'mysecretpassword',
};
const DEFAULT_API_RETURN_INFO = {
  users: [
    {
      userId: '111',
      userName: 'bobby@myforumapp.com',
      imageUrl: 'http://myforumwebapp.com',
      displayName: 'bobby',
    }
  ]
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

function createMockFetch(ok, status, jsonFunc) {
  const response = Promise.resolve({
    ok, status, json: jsonFunc
  });
  const mock = jest.fn()
    .mockName('Mocked fetch()')
    .mockImplementation( () => response );
  return mock;
}

function createErrorJsonData(msg) {
  return {
    error: {
      description: msg
    }
  };
}

// cleanup after every test case
afterEach(cleanup);

// suppress warnings
ReactModal.setAppElement('*');

describe('Testing behavior of login modal', () => {
  test('testing that all elements are rendered', () => {
    createModalWithMocks();

    screen.getByTitle(ModalLoginTitle);
    screen.getByAltText('modal input email');
    screen.getByAltText('modal input password');
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

  test('Login should send values in form to api', () => {
    createModalWithMocks();
    const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
    window.fetch = mockFetch;

    const { email, password } = DEFAULT_USERINFO;
    typeInputsAndClickLogin(email, password);

    expect(mockFetch.mock.calls).toHaveLength(1);
    const [ url, options ] = mockFetch.mock.calls[0];
    expect(url).toBe(userApiLogin);
    expect(options).toMatchObject({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify( { userName: email, password } ),
    });
  });

  test('Succesful login should store userinformation in user context', (done) => {
    const { mocks: { mockSetUser } } = createModalWithMocks();
    const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
    window.fetch = mockFetch;

    const { email, password } = DEFAULT_USERINFO;
    typeInputsAndClickLogin(email, password);

    // because fetch api is asynchronous, I need to use settimeout to catch the change
    setTimeout(() => {
      expect(mockSetUser.mock.calls).toHaveLength(1);
      expect(mockSetUser.mock.calls[0][0]).toEqual(DEFAULT_API_RETURN_INFO.users[0]);
      done();
    }, 50);
  });

  test('Succesful login should close modal', (done) => {
    const { mocks: { mockLogin } } = createModalWithMocks();
    const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
    window.fetch = mockFetch;

    const { email, password } = DEFAULT_USERINFO;
    typeInputsAndClickLogin(email, password);

    // because fetch api is asynchronous, I need to use settimeout to catch the change
    setTimeout(() => {
      expect(mockLogin.mock.calls).toHaveLength(1);
      done();
    }, 50);
  });

  test('Malformed email should show validation error notification under input', () => {
    const emailsToTry = [
      'bobby', 'bobby@', 123, 'bobby@123123', '@foo.com', '', '   ',
    ]

    for (let email of emailsToTry) {
      createModalWithMocks();
      const input = screen.getByAltText('modal input email');

      const { password } = DEFAULT_USERINFO;
      typeInputsAndClickLogin(email, password);

      getByText(input.parentElement, ERRORMSG_INVALID_EMAIL);
      cleanup();
    }
  });


  test('Invalid password should show validation error notification under input', () => {
    const passwordToTry = [
      '', '         ', '   password   ',
    ]

    for (let password of passwordToTry) {
      createModalWithMocks();
      const input = screen.getByAltText('modal input password');

      const { email } = DEFAULT_USERINFO;
      typeInputsAndClickLogin(email, password);

      getByText(input.parentElement, ERRORMSG_INVALID_PASSWORD);
      cleanup();
    }
  });

  test('Error notification should disappear after succesful validation', () => {
    const { email, password } = DEFAULT_USERINFO;
    const credentialsToTry = [
      { email: '', password },
      { email, password: '' },
    ]

    for (let credential in credentialsToTry) {
      createModalWithMocks();
      const mockFetch = createMockFetch(true, 200, () => Promise.resolve(DEFAULT_API_RETURN_INFO) );
      window.fetch = mockFetch;
      const emailInput = screen.getByAltText('modal input email');
      const passwordInput = screen.getByAltText('modal input password');

      // make error appear
      typeInputsAndClickLogin(credential.email, credential.password);
      typeInputsAndClickLogin(email, password);

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
    const emailInput = screen.getByAltText('modal input email');

    const { email, password } = DEFAULT_USERINFO;
    typeInputsAndClickLogin(email, password);

    await findByText(emailInput.parentElement, 'Invalid email for testing');
  });

  test('Failed password authentication should show warning under password input', async () => {
    createModalWithMocks();
    const mockFetch = createMockFetch(false, 400, () => 
      Promise.resolve( createErrorJsonData('Invalid password for testing') ) 
    );
    window.fetch = mockFetch;
    const passwordInput = screen.getByAltText('modal input password');

    const { email, password } = DEFAULT_USERINFO;
    typeInputsAndClickLogin(email, password);
    
    await findByText(passwordInput.parentElement, 'Invalid password for testing');
  });
});

// helper functions

// simulates user interaction with the login form
function typeInputsAndClickLogin(email, password) {
  const emailInput = screen.getByAltText('modal input email');
  const passwordInput = screen.getByAltText('modal input password');
  const loginButton = screen.getByTitle('login-button');

  const inputEvent = new Event('input', { bubbles: true });
  setNativeValue(emailInput, email);
  fireEvent.input(emailInput, inputEvent);
  setNativeValue(passwordInput, password);
  fireEvent.input(passwordInput, inputEvent);
  loginButton.click();
}

// sets value on controlled component
// https://stackoverflow.com/questions/40894637/how-to-programmatically-fill-input-elements-built-with-react
function setNativeValue(element, value) {
  const valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
  const prototype = Object.getPrototypeOf(element);
  const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;

  if (valueSetter && valueSetter !== prototypeValueSetter) {
    prototypeValueSetter.call(element, value);
  } else {
    valueSetter.call(element, value);
  }
}