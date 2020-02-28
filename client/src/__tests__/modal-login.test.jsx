import React from 'react';
import ReactModal from 'react-modal';
import {
  render, screen, cleanup, fireEvent, getByText
} from '@testing-library/react';

import ModalLogin, { ModalLoginTitle } from '../components/modal-login/modal-login.component';
import { ModalContext } from '../contexts/modal/modal';

afterEach(cleanup);
// suppress warnings
ReactModal.setAppElement('*');

function setupModalLogin(mockToggleLogin, mockToggleSignup) {
  return render(
    <ModalContext.Provider
      value={{
        isLoginOpen: true,
        toggleLogin: mockToggleLogin,
        toggleSignup: mockToggleSignup,
      }}
    >
      <div id='root'><ModalLogin /></div>
    </ModalContext.Provider>
  );
}

function createMockLoginToggle() {
  return jest.fn().mockName('Mocked toggleLogin()');
}

function createMockSignupToggle() {
  return jest.fn().mockName('Mocked toggleSignup()');
}

describe('Testing behavior of login modal', () => {
  test('testing that all elements are rendered', () => {
    const mockFunction = createMockLoginToggle();
    setupModalLogin(mockFunction);

    screen.getByTitle(ModalLoginTitle);
    screen.getByAltText('modal input email');
    screen.getByAltText('modal input password');
    screen.getByTitle('login-button')
    screen.getByTitle('google-login');
    screen.getByTitle('twitter-login');
    screen.getByTitle('link-signup-page');
  });

  test('clicking on the login button should call the api', () => {

  });

  test('clicking on the signup button should call toggleLogin and toggleSignup', () => {
    const mockLogin = createMockLoginToggle();
    const mockSignup = createMockSignupToggle();
    setupModalLogin(mockLogin, mockSignup);

    screen.getByTitle('link-signup-page').click();

    expect(mockLogin.mock.calls.length).toBe(1);
    expect(mockSignup.mock.calls.length).toBe(1);
  });

  test('Login should send values in form to api', () => {
    const mockLogin = createMockLoginToggle();
    const mockSignup = createMockSignupToggle();
    setupModalLogin(mockLogin, mockSignup);
  });

  test('Login failure should show warning under email input', () => {
    const mockLogin = createMockLoginToggle();
    const mockSignup = createMockSignupToggle();
    setupModalLogin(mockLogin, mockSignup);

    const email = screen.getByAltText('modal input email');
    getByText(email, 'Invalid username or password');
  });

  test('Failed password authentication should show warning under password input', () => {
    const mockLogin = createMockLoginToggle();
    const mockSignup = createMockSignupToggle();
    setupModalLogin(mockLogin, mockSignup);

    const password = screen.getByAltText('modal input password');
    getByText(password, 'Invalid username or password');
  });
});
