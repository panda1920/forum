import React from 'react';
import { act, screen, render, cleanup, getByText, fireEvent, wait } from '@testing-library/react';

import MenuDropdown from '../components/menu-dropdown/menu-dropdown.component';

import { CurrentUserContext } from '../contexts/current-user/current-user';
import { createMockFetch } from '../scripts/test-utilities';
import { userApiLogout } from '../paths';

const TEST_DATA = {
  TEST_USER: {
    userId: '11223344',
    userName: 'testuser@myforumwebappcom',
    displayName: 'testuser',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
  },
};

function createMenuDropdown() {
  const mockSetCurrentUser = createMockFunction('Mocked setCurrentUser()');
  const mockToggle = createMockFunction('Mocked toggle()');
  const renderResult = renderMenuDropdown(mockSetCurrentUser, mockToggle);

  return {
    ...renderResult,
    mocks: { mockSetCurrentUser, mockToggle }
  };
}

function renderMenuDropdown(setCurrentUser, toggleDropdown) {
  return render(
    <CurrentUserContext.Provider
      value={{ setCurrentUser }}
    >
      <MenuDropdown toggleDropdown={toggleDropdown} />
    </CurrentUserContext.Provider>
  );
}

function createMockFunction(name) {
  return jest.fn().mockName(name);
}

let originalFetch = null;
beforeEach(() => {
  originalFetch = window.fetch;
});
afterEach(() => {
  window.fetch = originalFetch;
  cleanup();
});

describe('testing behavior of menu dropdown component', () => {
  test('all sub elements should be rendrered as intended', () => {
    const { getByText } = createMenuDropdown();
    getByText('Edit Profile');
    getByText('Logout');
  });
  
  test('clicking on logout should invoke logout API call', async () => {
    createMenuDropdown();
    const mockFetch = createMockFetch(
      true, 200, () => Promise.resolve({ sessionUser: TEST_DATA.TEST_USER })
    );
    window.fetch = mockFetch;

    await clickLogout();

    expect(mockFetch).toBeCalledTimes(1);
    const [url, options ] = mockFetch.mock.calls[0];
    expect(url).toBe(userApiLogout);
    expect(options).toMatchObject({
      method: 'POST'
    });
  });
  
  test('successful logout should change user context', async () => {
    const { mocks: { mockSetCurrentUser } } = createMenuDropdown();
    window.fetch = createMockFetch(
      true, 200, () => Promise.resolve({ sessionUser: TEST_DATA.TEST_USER })
    );
    
    await clickLogout();

    expect(mockSetCurrentUser).toBeCalledTimes(1);
    const [ user ] = mockSetCurrentUser.mock.calls[0];
    expect(user).toMatchObject(TEST_DATA.TEST_USER);
  });
  
  test('failed logout should not change user context', async () => {
    const { mocks: { mockSetCurrentUser } } = createMenuDropdown();
    window.fetch = createMockFetch(
      false, 400, () => Promise.resolve({ message: 'failed api call'})
    );
    
    await clickLogout();

    expect(mockSetCurrentUser).toBeCalledTimes(0);
  });

  test('logout should call toggledropdown', async () => {
    const { mocks: { mockToggle } } = createMenuDropdown();
    window.fetch = createMockFetch(
      true, 200, () => Promise.resolve({ sessionUser: TEST_DATA.TEST_USER })
    );

    await clickLogout();

    expect(mockToggle).toHaveBeenCalled();
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

    expect(mockToggle).toHaveBeenCalled();
  });
});

async function clickLogout() {
  const dropdown = screen.getByTitle('dropdown');
  const logout = getByText(dropdown, 'Logout');

  // click implementation performs some async API calls
  await act(async () => {
    logout.click();
  });
}
