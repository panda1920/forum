import React from 'react';
import ReactModal from 'react-modal';
import {
    render,
    screen,
    cleanup,
    getByAltText,
    getByTitle,
    fireEvent
} from '@testing-library/react';
import { act } from 'react-dom/test-utils';

import { ModalContext } from '../contexts/modal/modal';
import { setNativeValue, createMockFetch } from '../scripts/test-utilities';
import { userApiLogin } from '../paths';

import ModalSignup, { ModalSignupTitle } from '../components/modal-signup/modal-signup.component';

const TEST_DATA = {
    DEFAULT_USERINFO: {
        email: 'bobby@myforumapp.com',
        password: 'mysecretpassword',
    },

};

const IDENTIFIERS = {
    EMAIL_ALT_TEXT: 'signup input email',
    PW_ALT_TEXT: 'signup input password',
    CONFIRM_ALT_TEXT: 'signup input confirm password',
    BUTTON_TITLE: 'signup-button',
    LINK_LOGIN_TITLE: 'link-login-page',
};

function renderSignup() {
    return render(
        <ModalContext.Provider
            value={{
                isSignupOpen: true
            }}
        >
            <div id='root'>
                <ModalSignup />
            </div>
        </ModalContext.Provider>
    );
}

let originalFetch = null;
beforeEach(() => {
    // here I want to take a backup of fetch so that I can restore later
    // this is because I am intending to mock this function during tests
    originalFetch = window.fetch;
})

afterEach(() => {
    cleanup();
    window.fetch = originalFetch;
});

// suppress warnings
ReactModal.setAppElement('*');

describe('Testing behavior of signup modal', () => {
    test('Subcomponents of signup modal should render on screen', () => {
        renderSignup();

        const signup = screen.getByTitle(ModalSignupTitle);
        getByAltText(signup, IDENTIFIERS.EMAIL_ALT_TEXT);
        getByAltText(signup, IDENTIFIERS.PW_ALT_TEXT);
        getByAltText(signup, IDENTIFIERS.CONFIRM_ALT_TEXT);
        getByTitle(signup, IDENTIFIERS.BUTTON_TITLE);
        getByTitle(signup, IDENTIFIERS.LINK_LOGIN_TITLE);
    });

    test('Typing into email input should change its value', async () => {
        renderSignup();
        const emailInput = screen.getByAltText(IDENTIFIERS.EMAIL_ALT_TEXT);

        const { email } = TEST_DATA.DEFAULT_USERINFO;
        typeEmail(email);

        expect(emailInput.value).toBe(email);
    });

    test('Typing into password input should change its value', async () => {
        renderSignup();
        const passwordInput = screen.getByAltText(IDENTIFIERS.PW_ALT_TEXT);

        const { password } = TEST_DATA.DEFAULT_USERINFO;
        typePassword(password);

        expect(passwordInput.value).toBe(password);
    });

    test('Typing into confirm password input should change its value', async () => {
        renderSignup();
        const confirmPasswordInput = screen.getByAltText(IDENTIFIERS.CONFIRM_ALT_TEXT);

        const { password } = TEST_DATA.DEFAULT_USERINFO;
        typeConfirmPassword(password);

        expect(confirmPasswordInput.value).toBe(password);
    });

    test('Pressing signup button should send API call with userinfo as body', async () => {
        renderSignup();
        const mockedFetch = createMockFetch(true, 200, () => {
            return Promise.resolve('some value');
        });
        window.fetch = mockedFetch;
        
        const { email, password } = TEST_DATA.DEFAULT_USERINFO;
        await typeInputAndSignup(email, password);

        expect(mockedFetch).toHaveBeenCalledTimes(1);
        const [ url, options ] = mockedFetch.mock.calls[0];
        expect(url).toBe(userApiLogin);
        expect(options).toMatchObject({
            body: JSON.stringify( { userName: email, password } )
        });
    });

    test('Successful signup should call signup with newly created user', () => {
        
    });
    
    test('Successful signup should close modal', () => {
        
    });

    test('Successful signup should clear input state', () => {
        
    });

    test('Invalid input should show error message on the corresponding input', () => {

    });
    
    test('Mismatch of password and confirm should show error on password input ', () => {

    });

    test('Error returned from API should show error message on email input', () => {

    });

    test('Error returned from API regarding password should show error message on password input', () => {

    });


});

// simulate user input

async function typeInputAndSignup(email, password) {
    typeEmail(email);
    typePassword(password);
    typeConfirmPassword(password);

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
    const signupButton = screen.getByTitle(IDENTIFIERS.BUTTON_TITLE);
    
    await act(async () => {
        signupButton.click();
    });
}
