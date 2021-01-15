import React from 'react';
import ReactModal from 'react-modal';
import {
    render,
    screen,
    cleanup,
    getByAltText,
    getByTitle,
    getByText,
    within,
    fireEvent
} from '@testing-library/react';
import { act } from 'react-dom/test-utils';

import { ModalContext } from '../../contexts/modal/modal';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import {
  setNativeValue,
  createMockFetch,
  createMockFetchImplementation,
  createErrorJsonData,
} from '../../scripts/test-utilities';
import { userApiLogin, userApiCreate } from '../../paths';

import ModalSignup, { ModalSignupTitle } from '../../components/modal-signup/modal-signup.component';

const TEST_DATA = {
  DEFAULT_USERINFO: {
    email: 'bobby@myforumwebapp.com',
    password: 'mysecretpassword',
  },

  SIGNUP_RETURNED_RESULT: {
    userCreated: 1,
  },

  API_RETURNED_SESSIONUSER: {
    userId: '11223344',
    userName: 'bobby@myforumwebapp.com',
    displayName: 'bobby',
    imageUrl: 'http://some_url_to_image.png',
  },
};

const IDENTIFIERS = {
  EMAIL_ALT_TEXT: 'signup input email',
  PW_ALT_TEXT: 'signup input password',
  CONFIRM_ALT_TEXT: 'signup input confirm password',
  SIGNUP_BUTTON_TITLE: 'signup button',
  CLOSE_BUTTON_TITLE: 'modal close button',
  LINK_LOGIN_TITLE: 'link login page',
};

// create signup dialog for a test case
function createSignup() {
  const mockSetCurrentUser = createMockFunction('Mocked setCurrentUser()');
  const mockToggleSignup = createMockFunction('Mocked toggleSignup()');
  const mockToggleLogin = createMockFunction('Mocked toggleLogin()');
  
  const renderResponse  = renderSignup(
    mockSetCurrentUser, mockToggleSignup, mockToggleLogin
  );

  return {
    ...renderResponse,
    mocks: { mockSetCurrentUser, mockToggleSignup, mockToggleLogin, }
  };
}
// render signup dialog
function renderSignup(mockSetCurrentUser, mockToggleSignup, mockToggleLogin) {
  return render(
    <CurrentUserContext.Provider
      value={{
        setCurrentUser: mockSetCurrentUser,
      }}
  >
      <ModalContext.Provider
        value={{
          isSignupOpen: true,
          toggleSignup: mockToggleSignup,
          toggleLogin: mockToggleLogin,
        }}
      >
        <div id='root'><ModalSignup /></div>
      </ModalContext.Provider>
    </CurrentUserContext.Provider>
  );
}

function createMockFunction(name) {
  return jest.fn().mockName(name);
}

function createMockFetchSuccess() {
  const mockFetch = jest.fn().mockName('Mocked fetch()')
    .mockImplementationOnce(createMockFetchImplementation(
      true, 201, () => Promise.resolve({ result: TEST_DATA.SIGNUP_RETURNED_RESULT })
    ))
    .mockImplementationOnce(createMockFetchImplementation(
      true, 200, () => Promise.resolve({ sessionUser: TEST_DATA.API_RETURNED_SESSIONUSER })
    ));

  return mockFetch;
}

let originalFetch = null;
beforeEach(() => {
  // here I want to take a backup of fetch so that I can restore later
  // this is because I am intending to mock this function during tests
  originalFetch = window.fetch;
  jest.useFakeTimers();
});

afterEach(() => {
  cleanup();
  window.fetch = originalFetch;
  jest.useRealTimers();
});

// suppress warnings
ReactModal.setAppElement('*');

describe('Testing behavior of signup modal', () => {
  test('Subcomponents of signup modal should render on screen', () => {
    createSignup();

    const signup = screen.getByTitle(ModalSignupTitle);
    getByAltText(signup, IDENTIFIERS.EMAIL_ALT_TEXT);
    getByAltText(signup, IDENTIFIERS.PW_ALT_TEXT);
    getByAltText(signup, IDENTIFIERS.CONFIRM_ALT_TEXT);
    getByTitle(signup, IDENTIFIERS.SIGNUP_BUTTON_TITLE);
    getByTitle(signup, IDENTIFIERS.LINK_LOGIN_TITLE);
  });

  test('Typing into email input should change its value', async () => {
    createSignup();
    const emailInput = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT);
    const { email } = TEST_DATA.DEFAULT_USERINFO;

    typeEmail(email);

    expect(emailInput.value).toBe(email);
  });

  test('Typing into password input should change its value', async () => {
    createSignup();
    const passwordInput = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT);
    const { password } = TEST_DATA.DEFAULT_USERINFO;

    typePassword(password);

    expect(passwordInput.value).toBe(password);
  });

  test('Typing into confirm password input should change its value', async () => {
    createSignup();
    const confirmPasswordInput = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT);
    const { password } = TEST_DATA.DEFAULT_USERINFO;

    typeConfirmPassword(password);

    expect(confirmPasswordInput.value).toBe(password);
  });

  test('Pressing signup button should send API call with userinfo as body', async () => {
    createSignup();
    const mockedFetch = createMockFetchSuccess();
    window.fetch = mockedFetch;
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    
    await typeInputAndSignup(email, password, password);

    expect(mockedFetch).toHaveBeenCalled();
    const [ url, options ] = mockedFetch.mock.calls[0];
    expect(url).toBe(userApiCreate);
    expect(options).toMatchObject({
      body: JSON.stringify( { userName: email, password } )
    });
  });

  test('Pressing signup button should call login after signup', async () => {
    createSignup();
    const mockedFetch = createMockFetchSuccess();
    window.fetch = mockedFetch;
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    
    await typeInputAndSignup(email, password, password);

    expect(mockedFetch).toHaveBeenCalled();
    const [ url, options ] = mockedFetch.mock.calls[1];
    expect(url).toBe(userApiLogin);
    expect(options).toMatchObject({
      body: JSON.stringify( { userName: email, password } )
    });
  });

  test('Successful signup should call setuser of usercontext with newly created user', async () => {
    const { mocks: { mockSetCurrentUser } } = createSignup();
    window.fetch = createMockFetchSuccess();
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;

    await typeInputAndSignup(email, password, password);

    expect(mockSetCurrentUser).toHaveBeenCalledTimes(1);
    const currentUser = mockSetCurrentUser.mock.calls[0][0];
    expect(currentUser).toMatchObject(TEST_DATA.API_RETURNED_SESSIONUSER);
  });
  
  test('Successful signup should close modal', async () => {
    const { mocks: { mockToggleSignup } } = createSignup();
    window.fetch = createMockFetchSuccess();
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;

    await typeInputAndSignup(email, password, password);

    expect(mockToggleSignup).toHaveBeenCalledTimes(1);
  });

  test('Successful signup should clear input state', async () => {
    createSignup();
    window.fetch = createMockFetchSuccess();
    const emailInput = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT);
    const passwordInput = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT);
    const confirmPasswordInput = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT);
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;

    await typeInputAndSignup(email, password, password);

    expect(emailInput.value).toBe('');
    expect(passwordInput.value).toBe('');
    expect(confirmPasswordInput.value).toBe('');
  });

  test('Invalid email should show error on email input', async () => {
    createSignup();
    window.fetch = createMockFetchSuccess();
    const emailInputContainer = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT).parentElement;
    const emailsToTest = [
      '',
      ' ',
      'bobby',
      '@myforumwebapp.com',
      'bobby@myforumwebapp',
      'bobby @myforumwebapp.com',
      ' bobby@myforumwebapp.com',
      'bobby@myforumwebapp.com ',
    ];
    const { password } = TEST_DATA.DEFAULT_USERINFO;

    for (const email of emailsToTest) {
      await typeInputAndSignup(email, password, password);

      getByText(emailInputContainer, 'Invalid email');
    }
  });

  test('Invalid password should show error on password input', async () => {
    createSignup();
    window.fetch = createMockFetchSuccess();
    const passwordInputContainer = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT).parentElement;
    const passwordsToTest = [
      '',
      ' ',
      ' mysecretpassword',
      'mysecretpassword ',
      'my secretpassword',
    ];
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;

    for (const badPassword of passwordsToTest) {
      await typeInputAndSignup(email, badPassword, password);

      getByText(passwordInputContainer, 'Invalid password');
    }
  });
  
  test('Mismatch of password and confirm should show error on confirm input', async () => {
    createSignup();
    window.fetch = createMockFetchSuccess();
    const confirmPasswordInputContainer = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT).parentElement;
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const confirmPassword = 'not_the_same';

    await typeInputAndSignup(email, password, confirmPassword);

    getByText(confirmPasswordInputContainer, 'Passwords did not match');
  });
  
  test('Invalid input should not call the API ', async () => {
    createSignup();
    const mockedFetch = createMockFetchSuccess();
    window.fetch = mockedFetch;
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const invalidInputs = [
      { email, password: '', confirmPassword: password },
      { email: '', password, confirmPassword: password },
      { email, password, confirmPassword: '' },
    ];

    for (const input of invalidInputs) {
      await typeInputAndSignup(input.email, input.password, input.confirmPassword);

      expect(mockedFetch).not.toHaveBeenCalled();
    }
  });

  test('Clicking signup should clear error message of previous attempt', async () => {
    createSignup();
    window.fetch = createMockFetchSuccess();
    const emailInputContainer = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT).parentElement;
    const passwordInputContainer = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT).parentElement;
    const confirmInputContainer = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT).parentElement;
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const invalidInputs = [
      { email, password: '', confirmPassword: password },
      { email: '', password, confirmPassword: password },
      { email, password, confirmPassword: '' },
    ];
    const nodesToExpectError = [
      passwordInputContainer, emailInputContainer, confirmInputContainer,
    ];

    for (let i = 0; i < invalidInputs.length; ++i) {
      const input = invalidInputs[i];
      const nextInput = invalidInputs[(i + 1) % invalidInputs.length];
      const expectedNode = nodesToExpectError[i];
      
      await typeInputAndSignup(input.email, input.password, input.confirmPassword);
      act( () => jest.advanceTimersByTime(1000) );
      await typeInputAndSignup(nextInput.email, nextInput.password, nextInput.password);

      const errorMsg = within(expectedNode).queryByText(/^Invalid|Passwords/);
      expect(errorMsg).toBeNull();
    }
  });

  test('Error returned from API should show error message on email input', async () => {
    createSignup();
    const errorMsg = 'Email already registered';
    window.fetch = createMockFetch(false, 400, () => {
      return createErrorJsonData(errorMsg);
    });
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const emailInputContainer = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT).parentElement;

    await typeInputAndSignup(email, password, password);

    within(emailInputContainer).getByText(errorMsg);
  });

  test('Error returned from API regarding password should show error message on password input', async () => {
    createSignup();
    const errorMsg = 'Wrong password';
    window.fetch = createMockFetch(false, 400, () => {
      return createErrorJsonData(errorMsg);
    });
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const passwordInputContainer = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT).parentElement;

    await typeInputAndSignup(email, password, password);

    within(passwordInputContainer).getByText(errorMsg);
  });

  test('Error returned from API with statuscode >=500 should show no error', async () => {
    createSignup();
    const errorMsg = 'Email already registered';
    window.fetch = createMockFetch(false, 500, () => {
      return createErrorJsonData(errorMsg);
    });
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const emailInputContainer = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT).parentElement;

    await typeInputAndSignup(email, password, password);

    expect( within(emailInputContainer).queryByText(errorMsg) ).toBeNull();
  });

  test('Failed API call should not close dialog', async () => {
    const { mocks: { mockToggleSignup } } = createSignup();
    const errorMsg = 'Email already registered';
    window.fetch = createMockFetch(false, 400, () => {
      return createErrorJsonData(errorMsg);
    });
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;

    await typeInputAndSignup(email, password, password);

    expect(mockToggleSignup).not.toHaveBeenCalled();
  });

  test('Failed API call should not clear input value', async () => {
    createSignup();
    const errorMsg = 'Email already registered';
    window.fetch = createMockFetch(false, 400, () => {
      return createErrorJsonData(errorMsg);
    });
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const emailInput = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT);
    const passwordInput = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT);
    const confirmInput = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT);

    await typeInputAndSignup(email, password, password);

    expect(emailInput.value).toBe(email);
    expect(passwordInput.value).toBe(password);
    expect(confirmInput.value).toBe(password);
  });

  test('Closing modal dialog should reset input state', async () => {
    createSignup();
    const errorMsg = 'Email already registered';
    window.fetch = createMockFetch(false, 400, () => {
      return createErrorJsonData(errorMsg);
    });
    const { email, password } = TEST_DATA.DEFAULT_USERINFO;
    const emailInput = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT);
    const passwordInput = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT);
    const confirmInput = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT);

    await typeInputAndSignup(email, password, password);
    clickClose();

    expect(emailInput.value).toBe('');
    expect(passwordInput.value).toBe('');
    expect(confirmInput.value).toBe('');
    expect( within(emailInput.parentElement).queryByText(errorMsg) ).toBeNull();
  });

  test('Clicking on link should close signup dialog and open login dialog', () => {
    const { mocks: { mockToggleSignup, mockToggleLogin } } =  createSignup();
    window.fetch = createMockFetchSuccess();

    clickLogin();

    expect(mockToggleSignup).toHaveBeenCalledTimes(1);
    expect(mockToggleLogin).toHaveBeenCalledTimes(1);
  });
});

// simulate user input

async function typeInputAndSignup(email, password, confirmPassword) {
  typeEmail(email);
  typePassword(password);
  typeConfirmPassword(confirmPassword);

  await clickSignup();
}

function typeEmail(email) {
  typeToInput(email, IDENTIFIERS.EMAIL_ALT_TEXT);
}

function typePassword(password) {
  typeToInput(password, IDENTIFIERS.PW_ALT_TEXT);
}

function typeConfirmPassword(password) {
  typeToInput(password, IDENTIFIERS.CONFIRM_ALT_TEXT);
}

function typeToInput(inputString, alt) {
  const input = screen.getByAltText(alt);
  const inputEvent = new Event('input', { bubbles: true });

  act(() => {
    setNativeValue(input, inputString);
    fireEvent.input(input, inputEvent);
  });
}

async function clickSignup() {
  const signupButton = screen.getByTitle(IDENTIFIERS.SIGNUP_BUTTON_TITLE);
  
  await act(async () => {
    signupButton.click();
  });
}

function clickClose() {
  const closeButton = screen.getByTitle(IDENTIFIERS.CLOSE_BUTTON_TITLE);
  act(() => {
    closeButton.click();
  });
}

function clickLogin() {
  const loginButton = screen.getByTitle(IDENTIFIERS.LINK_LOGIN_TITLE);
  act(() => {
    loginButton.click();
  });
}
