import React from 'react';
import { Route, Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { act, screen, render, cleanup, getByText, fireEvent } from '@testing-library/react';
import UserEvent from '@testing-library/user-event';

import MenuDropdown from '../components/menu-dropdown/menu-dropdown.component';
import { CurrentUserContext } from '../contexts/current-user/current-user';

import { createMockFetch } from '../scripts/test-utilities';
import { userApiLogout, clientUserProfilePath } from '../paths';
import { logout } from '../scripts/api';
import { createMockFetchImplementation } from '../scripts/test-utilities';

// mock out functions
jest.mock('../scripts/api', () => {
  return {
    logout: jest.fn().mockName('mocked logout()'),
  };
});

const TEST_DATA = {
  TEST_USER: {
    userId: '11223344',
    userName: 'testuser@myforumwebappcom',
    displayName: 'testuser',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
  },
  DEFAULT_URL: '/test/path',
};

function createMenuDropdown() {
  const mockSetCurrentUser = jest.fn().mockName('Mocked setCurrentUser()');
  const mockToggle = jest.fn().mockName('Mocked toggle()');
  const history = createMemoryHistory({
    initialEntires: [ TEST_DATA.DEFAULT_URL ]
  });
  const renderResult = renderMenuDropdown(mockSetCurrentUser, mockToggle, history);

  return {
    ...renderResult,
    history,
    mocks: { mockSetCurrentUser, mockToggle }
  };
}

function renderMenuDropdown(setCurrentUser, toggleDropdown, history) {
  return render(
    <Router history={history}>
      <CurrentUserContext.Provider
        value={{ ...TEST_DATA.TEST_USER, setCurrentUser }}
      >
        <Route path='/'>
          <MenuDropdown toggleDropdown={toggleDropdown} />
        </Route>
      </CurrentUserContext.Provider>
    </Router>
  );
}

beforeEach(() => {
  logout.mockImplementation(
    createMockFetchImplementation(true, 200, async () => (
      { sessionUser: TEST_DATA.TEST_USER }
    ))
  );
});
afterEach(() => {
  cleanup();
  logout.mockClear();
});

describe('testing behavior of menu dropdown component', () => {
  test('all sub elements should be rendrered as intended', () => {
    const { getByText } = createMenuDropdown();

    expect( getByText('User Profile') ).toBeInTheDocument();
    expect( getByText('Logout') ).toBeInTheDocument();

    // user info should rendered as well
    expect( getByText(TEST_DATA.TEST_USER.displayName) ).toBeInTheDocument();
    expect( getByText(TEST_DATA.TEST_USER.userName) ).toBeInTheDocument();
  });
  
  test('Clicking on logout should invoke logout API call', async () => {
    createMenuDropdown();

    await clickLogout();

    expect(logout).toBeCalledTimes(1);
  });
  
  test('Successful logout should change user context to user returned from api', async () => {
    const { mocks: { mockSetCurrentUser } } = createMenuDropdown();
    
    await clickLogout();

    expect(mockSetCurrentUser).toBeCalledTimes(1);
    const [ user ] = mockSetCurrentUser.mock.calls[0];
    expect(user).toMatchObject(TEST_DATA.TEST_USER);
  });
  
  test('failed logout should not change user context', async () => {
    const { mocks: { mockSetCurrentUser } } = createMenuDropdown();
    logout.mockImplementation(
      createMockFetchImplementation(false, 400, async () => {})
    );
    
    await clickLogout();

    expect(mockSetCurrentUser).toBeCalledTimes(0);
  });

  test('Successful logout should call toggledropdown', async () => {
    const { mocks: { mockToggle } } = createMenuDropdown();

    await clickLogout();

    expect(mockToggle).toHaveBeenCalledTimes(2);
  });

  test('menu dropdown rendered should gain focus', () => {
    createMenuDropdown();
    const dropdown = screen.getByTitle('dropdown');

    expect(document.activeElement).toBe(dropdown);
  });

  test('when menu dropdown lose focus should fire toggle dropdown', () => {
    const { mocks: { mockToggle } } = createMenuDropdown();
    const dropdown = screen.getByTitle('dropdown');
    const blurevent = new FocusEvent('blur');

    act(() => {
      fireEvent(dropdown, blurevent);
    });

    expect(mockToggle).toHaveBeenCalledTimes(1);
  });

  test('Should transition to user page when userinfo is clicked', () => {
    const { history, getByText } = createMenuDropdown();
    const userInfo = getByText('User Profile');

    UserEvent.click(userInfo);

    expect(history.location.pathname).toBe(clientUserProfilePath);
  });

  test('Should invoke toggleDropdown when transition to user page', () => {
    const { getByText, mocks: { mockToggle } } = createMenuDropdown();
    const userInfo = getByText('User Profile');

    UserEvent.click(userInfo);

    expect(mockToggle).toHaveBeenCalledTimes(2);
  });
});

async function clickLogout() {
  const dropdown = screen.getByTitle('dropdown');
  const logout = getByText(dropdown, 'Logout');

  await act(async () => UserEvent.click(logout));
}
