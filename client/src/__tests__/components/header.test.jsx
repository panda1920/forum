import React from 'react';
import { screen, render, act, cleanup, getByTitle } from '@testing-library/react';

import Header from '../../components/header/header.component';
import MenuDropdown from '../../components/menu-dropdown/menu-dropdown.component';

import { CurrentUserContext } from '../../contexts/current-user/current-user';

// mock out child components
jest.mock('../../components/menu-dropdown/menu-dropdown.component', () => {
  return {
    __esModule: true,
    default: jest.fn().mockName('mocked MenuDropdown()')
      .mockImplementation(() => <div title='dropdown' />)
  };
});

const TEST_DATA = {
  TEST_USER_ANONYMOUS: {
    userId: '0',
    userName: 'anonymous@myforumwebappcom',
    displayName: 'anonymous',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
    isLoggedin: () => false,
  },
  TEST_USER: {
    userId: '11223344',
    userName: 'testuser@myforumwebappcom',
    displayName: 'testuser',
    imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
    isLoggedin: () => true,
  },
};

const ELEMENT_IDENTIFIER = {
  HEADER_TITLE: 'header',
  HEADER_PORTRAIT_TITLE: 'header portrait',
  DROPDOWN_TITLE: 'dropdown',
};

function createLoggedoutHeader() {
  return renderHeader(TEST_DATA.TEST_USER_ANONYMOUS);
}

function createLoggedinHeader() {
  return renderHeader(TEST_DATA.TEST_USER);
}

function renderHeader(user) {
  const renderResponse = render(
    <CurrentUserContext.Provider
      value={{
        ...user,
      }}
    >
      <Header/>
    </CurrentUserContext.Provider>
  );
    
  return {
    ...renderResponse
  };
}

afterEach(cleanup);
  
describe('Tests for Header component', () => {
    test('sub-components should be rendered when user not logged in', () => {
        const { queryByTitle, getByText } = createLoggedoutHeader();

        getByText('MYFORUMAPP');
        getByText('SIGNUP');
        getByText('LOGIN');
        expect( queryByTitle(ELEMENT_IDENTIFIER.HEADER_PORTRAIT_TITLE) )
          .toBeNull();
    });

    test('sub-components should be rendered when user is logged in', () => {
        const { getByText, getByTitle, queryByText, queryByTitle } = createLoggedinHeader();

        getByText('MYFORUMAPP');
        expect( queryByText('SIGNUP') ).toBeNull();
        expect( queryByText('LOGIN') ).toBeNull();
        getByTitle(ELEMENT_IDENTIFIER.HEADER_PORTRAIT_TITLE);
        expect( queryByTitle(ELEMENT_IDENTIFIER.DROPDOWN_TITLE) ).toBeNull();
    });

    test('clicking on portrait when logged in should make dropdown visible', () => {
      const { getByTitle } = createLoggedinHeader();

      clickOnHeaderPortrait();

      getByTitle(ELEMENT_IDENTIFIER.DROPDOWN_TITLE);
    });
});

// simulate user interaction with app
function clickOnHeaderPortrait() {
  const header = screen.getByTitle(ELEMENT_IDENTIFIER.HEADER_TITLE);
  const portrait = getByTitle(header, ELEMENT_IDENTIFIER.HEADER_PORTRAIT_TITLE);

  act(() => {
    portrait.click();
  });
}
