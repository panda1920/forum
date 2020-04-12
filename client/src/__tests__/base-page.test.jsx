import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { render, screen, cleanup, getByText, act, wait } from '@testing-library/react';

import BasePage from '../pages/base/base-page.component';
import { ModalLoginTitle } from '../components/modal-login/modal-login.component';
import { ModalSignupTitle } from '../components/modal-signup/modal-signup.component';

import { CurrentUserContext, INITIAL_STATE } from '../contexts/current-user/current-user';
import { userApiSession } from '../paths';
import { createMockFetch, } from  '../scripts/test-utilities';

// mock out child components
jest.mock('../pages/board/board-page.component');

const TEST_DATA = {
  SESSION_USER: {
    userId: '11223344',
    userName: 'testuser@myforumwebappcom',
    displayName: 'testuser',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
  },
};

const ELEMENT_IDENTIFIER = {
  HEADER_TITLE: 'header',
  FOOTER_TITLE: 'footer',
  LOGIN_BUTTON_TEXT: 'LOGIN',
  SIGNUP_BUTTON_TEXT: 'SIGNUP',
  BOARD_PAGE_TITLE: 'board page',
};

function renderBasePage() {
  const mockSetCurrentUser = jest.fn().mockName('Mocked setCurrentUser()');
  const userContextValue = { ...INITIAL_STATE, setCurrentUser: mockSetCurrentUser };

  const result = render(
    <BrowserRouter>
      <div id='root'>
        <CurrentUserContext.Provider
          value={ userContextValue }
        >
          <BasePage />
        </CurrentUserContext.Provider>
      </div>
    </BrowserRouter>
  );

  return {
    ...result,
    mockSetCurrentUser,
  };
}

function createFetchSuccess() {
  return  createMockFetch(true, 200, () => {
    return Promise.resolve({ sessionUser: TEST_DATA.SESSION_USER });
  });
}

let originalFetch = null;
beforeEach(() => {
  originalFetch = window.fetch;
  window.fetch = createFetchSuccess();
});
afterEach(() => {
  window.fetch = originalFetch;
  cleanup();
});

describe('Testing BasePage', () => {
  test('All sub component of basepage should be rendered', () => {
    const { getByTitle } = renderBasePage();

    getByTitle(ELEMENT_IDENTIFIER.HEADER_TITLE);
    getByTitle(ELEMENT_IDENTIFIER.FOOTER_TITLE);
  });

  test('Base page should render board page by default', () => {
    const { getByTitle } = renderBasePage();

    getByTitle(ELEMENT_IDENTIFIER.BOARD_PAGE_TITLE);
  });

  test('Clicking on login should blur the page', () => {
    const { container } = renderBasePage();
    const getBasePageClasses = () => {
      return container.firstChild.firstChild.getAttribute('Class').split(' ');
    };

    expect( getBasePageClasses() ).not.toContain('blurred');

    clickHeaderLogin();

    expect( getBasePageClasses() ).toContain('blurred');
  });

  test('Clicking on login should bring up modal', () => {
    renderBasePage();

    expect( screen.queryByTitle(ModalLoginTitle) ).toBeNull();

    clickHeaderLogin();

    expect( screen.queryByTitle(ModalLoginTitle) ).not.toBeNull();
  });

  test('Clicking on signup should blur the page', () => {
    const { container } = renderBasePage();
    const getBasePageClasses = () => {
      return container.firstChild.firstChild.getAttribute('Class').split(' ');
    };

    expect( getBasePageClasses() ).not.toContain('blurred');

    clickHeaderSignup();

    expect( getBasePageClasses() ).toContain('blurred');
  });

  test('Clicking on signup should bring up modal', () => {
    renderBasePage();

    expect( screen.queryByTitle(ModalSignupTitle) ).toBeNull();

    clickHeaderSignup();

    expect( screen.queryByTitle(ModalSignupTitle) ).not.toBeNull();
  });

  test('Base page should call user session api when loaded', async () => {
    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    renderBasePage();

    // async operation in useeffect of base page
    // sometimes assertions fail because promise is not resolved when test runs
    // which is why async wait is being used here
    await wait(() => {
      expect(mockFetch).toHaveBeenCalled();
      const [ url, options ] = mockFetch.mock.calls[0];
      expect(url).toBe(userApiSession);
      expect(options).toMatchObject({ method: 'GET' });
    });
  });

  test('Base page should set user context by the returned value from session user api', async () => {
    const { mockSetCurrentUser } = renderBasePage();

    await wait(() => {
      expect(mockSetCurrentUser).toHaveBeenCalledWith(TEST_DATA.SESSION_USER);
    });
  });

  test('Base page should not set user context when api call fails', async () => {
    const mockFetch = createMockFetch(false, 400, () =>
      Promise.resolve({ errorMessage: 'Failed to retrieve session' })
    );
    window.fetch = mockFetch;
    const { mockSetCurrentUser } = renderBasePage();

    await wait(() => {
      expect(mockFetch).toHaveBeenCalled();
      expect(mockSetCurrentUser).not.toHaveBeenCalled();
    });
  });
});

// simulate user interaction with UI
function clickHeaderLogin() {
  const header = screen.getByTitle(ELEMENT_IDENTIFIER.HEADER_TITLE);
  const login = getByText(header, ELEMENT_IDENTIFIER.LOGIN_BUTTON_TEXT);

  act(() => {
    login.click();
  });
}

function clickHeaderSignup() {
  const header = screen.getByTitle(ELEMENT_IDENTIFIER.HEADER_TITLE);
  const signup = getByText(header, ELEMENT_IDENTIFIER.SIGNUP_BUTTON_TEXT);

  act(() => {
    signup.click();
  });
}