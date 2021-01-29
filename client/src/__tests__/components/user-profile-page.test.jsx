import React from 'react';
import { Router } from 'react-router-dom';
import { render, cleanup, act, screen } from '@testing-library/react';
import { createMemoryHistory } from 'history';

import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import UserProfile from '../../pages/user-profile/user-profile-page';
import Spinner from '../../components/spinner/spinner.component';
import ProfileFieldText from '../../components/profile-field/profile-field-text.component';
import ProfileFieldPassword from '../../components/profile-field/profile-field-password.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

// mock out subcomponents
jest.mock('../../components/breadcrumbs/breadcrumbs.component');
jest.mock('../../components/spinner/spinner.component');
jest.mock('../../components/profile-field/profile-field-password.component');
jest.mock('../../components/profile-field/profile-field-text.component');


const TEST_DATA = {
  CURRENT_USER: {
    displayName: 'Bobby',
    userName: 'Bobby@example.com',
    userId: 'test_userid',
    imageUrl: 'www.example.com/user.jpeg',
  },
  DEFAULT_URL: '/some/path',
};

const IDENTIFIERS = {
  DISPLAYNAME_FIELD_ID: 'displayName',
  PASSWORD_FIELD_ID: 'password',
};

async function renderUserProfile(options = {}) {
  let { isLoggedin, beforeFetch } = options;
  // default options
  if (isLoggedin === undefined)
    isLoggedin = true;
  if (beforeFetch === undefined)
    beforeFetch = false;

  const memoryHistory = createMemoryHistory({
    initialEntries: [ TEST_DATA.DEFAULT_URL ]
  });

  let renderResult;
  await act(async () => renderResult = render(
    <Router history={memoryHistory}>
      <CurrentUserContext.Provider
        value={{...TEST_DATA.CURRENT_USER, beforeFetch, isLoggedin: () => isLoggedin }}
      >
        <UserProfile />
      </CurrentUserContext.Provider>
    </Router>
  ));

  return {
    ...renderResult,
    history: memoryHistory,
  };
}


beforeEach(() => {

});

afterEach(() => {
  cleanup();
  Breadcrumbs.mockClear();
  Spinner.mockClear();
  ProfileFieldText.mockClear();
  ProfileFieldPassword.mockClear();
});

describe('Testing UserProfile to render subcomponents', () => {
  test('Renders page title', async () => {
    const pageTitle = 'User Profile';

    const { getByText } = await renderUserProfile();

    expect( getByText(pageTitle) ).toBeInTheDocument();
  });
  
  test('Renders Breadcrumbs', async () => {
    await renderUserProfile();

    expect(Breadcrumbs).toHaveBeenCalledTimes(1);
  });
  
  test('Renders UserInfo fields', async () => {
    await renderUserProfile();

    expect( screen.getByTestId(IDENTIFIERS.DISPLAYNAME_FIELD_ID) )
      .toBeInTheDocument();
    expect( screen.getByTestId(IDENTIFIERS.PASSWORD_FIELD_ID) )
      .toBeInTheDocument();
  });

  test('Renders only Spinner while waiting for usercontext to populate', async () => {
    const pageTitle = 'User info';

    const { queryByText } = await renderUserProfile({ beforeFetch: true });

    expect(Spinner).toHaveBeenCalledTimes(1);
    expect(Breadcrumbs).not.toHaveBeenCalled();
    expect( queryByText(pageTitle) ).not.toBeInTheDocument();
    expect(ProfileFieldText).not.toHaveBeenCalled();
    expect(ProfileFieldPassword).not.toHaveBeenCalled();
  });
});

describe('Testing behavior of UserProfile', () => {
  test('Should redirect back to root page when not logged in', async () => {
    const { history } = await renderUserProfile({ isLoggedin: false });

    expect(history.location.pathname).toBe('/');
  });

  test('Should pass link definitions to Breadcrumbs', async () => {
    const expectedLinkDefinitions = [
      { displayName: 'Home', path: '/' },
      { displayName: 'User Profile', path: null },
    ];

    await renderUserProfile();

    for(const call of Breadcrumbs.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('links');
      expect(props.links).toMatchObject(expectedLinkDefinitions);
    }
  });

  test('Should pass user information to displayName field', async () => {
    await renderUserProfile();

    const displayNameComponentCall = ProfileFieldText.mock.calls.find(call => {
      return call[0]['data-testid'] === IDENTIFIERS.DISPLAYNAME_FIELD_ID;
    });
    const [ props ] = displayNameComponentCall;

    expect(props).toHaveProperty('fieldname', 'Display Name');
    expect(props).toHaveProperty('fieldid', 'displayName');
    expect(props).toHaveProperty('value', TEST_DATA.CURRENT_USER.displayName);
  });
});
