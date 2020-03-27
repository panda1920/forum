import React from 'react';
import { render, act, cleanup, getByAltText } from '@testing-library/react';
import { toBeVisible } from '@testing-library/jest-dom';

import Header from '../components/header/header.component';

import { CurrentUserContext } from '../contexts/current-user/current-user';

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
  HEADER_ID: 'header',
  HEADER_PORTRAIT_ALT_TEXT: 'portrait image of user',
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
        const { container, queryByAltText, getByText } = createLoggedoutHeader();

        getByText('MYFORUMAPP');
        getByText('SIGNUP');
        getByText('LOGIN');
        expect( queryByAltText(ELEMENT_IDENTIFIER.HEADER_PORTRAIT_ALT_TEXT) )
          .toBeNull();
    });

    test('sub-components should be rendered when user is logged in', () => {
        const { container, getByText, getByAltText, queryByText, queryByTitle } = createLoggedinHeader();

        getByText('MYFORUMAPP');
        expect( queryByText('SIGNUP') ).toBeNull();
        expect( queryByText('LOGIN') ).toBeNull();
        getByAltText(ELEMENT_IDENTIFIER.HEADER_PORTRAIT_ALT_TEXT);
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
  const header = document.querySelector(`#${ELEMENT_IDENTIFIER.HEADER_ID}`);
  const portrait = getByAltText(header, ELEMENT_IDENTIFIER.HEADER_PORTRAIT_ALT_TEXT);

  act(() => {
    portrait.click();
  });
}