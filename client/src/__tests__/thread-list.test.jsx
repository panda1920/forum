import React from 'react';
import { screen, render, cleanup, act } from '@testing-library/react';

import * as paths from '../paths';
import { createMockFetch } from '../scripts/test-utilities';

import { CurrentUserContext } from '../contexts/current-user/current-user';

import ThreadCard from '../components/thread-card/thread-card.component';
import ThreadList from '../components/thread-list/thread-list.component';

// mock out child component
jest.mock('../components/thread-card/thread-card.component');

const IDENTIFIERS = {
  TITLE_THREAD_CARD: 'thread card',
  TITLE_THREADS: 'threads',
  TITLE_THREADS_HEADER: 'threads header',
  TITLE_PAGINATION_BAR: 'pagination bar',
  TITLE_BUTTON_FIRST: 'pagination button first',
  TITLE_BUTTON_BACK: 'pagination button back',
  TITLE_BUTTON_NEXT: 'pagination button next',
  TITLE_BUTTON_LAST: 'pagination button last',
};

const TEST_DATA = {
  BOARD_ID: '0',
  PAGE_SIZE: 2,
  API_RETURN_SESSIONUSER: {
    userId: '1',
    userName: 'testuser@myforumwebapp.com',
  },
  API_RETURN_RESULT: {
    threads: [
      {
        boardId: '1',
        threadId: '0',
        userId: '2',
        title: 'test thread title 0'
      },
      {
        boardId: '1',
        threadId: '1',
        userId: '3',
        title: 'test thread title 1'
      },
    ],
    returnCount: 2,
    matchedCount: 5,
  },
};

async function createThreadList() {
  const mockSetCurrentUser = jest.fn().mockName('Mocked setCurrentUser()');
  let renderResult;
  
  await act(async () => {
    renderResult = render(
      <CurrentUserContext.Provider
        value={{ setCurrentUser: mockSetCurrentUser }}
      >
        <ThreadList
          boardId={TEST_DATA.BOARD_ID}
          pageSize={TEST_DATA.PAGE_SIZE}
        />
      </CurrentUserContext.Provider>
    );
  });
  
  return {
    ...renderResult,
    mocks: { mockSetCurrentUser },
  };
}

function createFetchSuccess() {
  return createMockFetch(true, 200, () =>
    Promise.resolve({
      result: TEST_DATA.API_RETURN_RESULT,
      sessionUser: TEST_DATA.API_RETURN_SESSIONUSER,
    })
  );
}

let originalFetch = null;
beforeEach(() => {
  originalFetch = window.fetch;
  window.fetch = createFetchSuccess();
});
afterEach(() => {
  cleanup();
  ThreadCard.mockClear();
  window.fetch = originalFetch;
});

describe('testing behavior of ThreadList component', () => {
  test('subcomponents should be rendered', async () => {
    const { getAllByTitle } = await createThreadList();
    
    const paginations = getAllByTitle(IDENTIFIERS.TITLE_PAGINATION_BAR);
    expect(paginations).toHaveLength(2);
    getAllByTitle(IDENTIFIERS.TITLE_THREAD_CARD);
    getAllByTitle(IDENTIFIERS.TITLE_THREADS);
    getAllByTitle(IDENTIFIERS.TITLE_THREADS_HEADER);
  });

  
  test('upon rendering should search threads related to boardId', async () => {
    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    const expectedEndpoint = paths.threadApi;
    const expectedQuerystring = `?boardId=${TEST_DATA.BOARD_ID}&offset=0&limit=${TEST_DATA.PAGE_SIZE}`;
    await createThreadList();

    expect(mockFetch).toHaveBeenCalled();
    const [ url, options ] = mockFetch.mock.calls[0];
    expect(url).toBe(`${expectedEndpoint}${expectedQuerystring}`);
    expect(options).toMatchObject({
      method: 'GET',
    });
  });

  test('upon rendering should set current user state from return value of api call', async () => {
    const { mocks: { mockSetCurrentUser } } = await createThreadList();

    expect(mockSetCurrentUser).toHaveBeenCalled();
    const [ userinfo ] = mockSetCurrentUser.mock.calls[0];
    expect(userinfo).toMatchObject(TEST_DATA.API_RETURN_SESSIONUSER);
  });

  test('upon rendering should render threads returned from api as thread cards', async () => {
    expect(ThreadCard.mock.calls).toHaveLength(0);
    
    const { getAllByTitle } = await createThreadList();

    const threadCards = getAllByTitle(IDENTIFIERS.TITLE_THREAD_CARD);
    expect(threadCards).toHaveLength(TEST_DATA.API_RETURN_RESULT.threads.length);
    const propsPassed = ThreadCard.mock.calls.map(call => call[0]);
    propsPassed.forEach((prop, idx) => {
      expect(prop).toHaveProperty('thread');
      expect(prop.thread).toMatchObject(TEST_DATA.API_RETURN_RESULT.threads[idx]);
    });
  });
});

describe('testing behavior of pagination bar', () => {
  test('upon render should render text explaining how much of search result is displayed', async ()=> {
    const { getAllByText } = await createThreadList();

    const displayCount = TEST_DATA.API_RETURN_RESULT.returnCount;
    const total = TEST_DATA.API_RETURN_RESULT.matchedCount;
    const displayText = getAllByText( new RegExp(`.*Displaying 1-${displayCount} of ${total}.*`) );
    expect(displayText).toHaveLength(2);
  });

  test('upon render first and back buttons should be disabled', async () => {
    const { getAllByTitle } = await createThreadList();

    const firstButtons = getAllByTitle(IDENTIFIERS.TITLE_BUTTON_FIRST);
    firstButtons.forEach(button => {
      const classes = button.className.split(' ');
      expect(classes).toContain('button-disabled');
    });
    const backButtons = getAllByTitle(IDENTIFIERS.TITLE_BUTTON_BACK);
    backButtons.forEach(button => {
      const classes = button.className.split(' ');
      expect(classes).toContain('button-disabled');
    });
  });

  test('first and back buttons should be active after clicking next button', async () => {
    const { getAllByTitle } = await createThreadList();

    await clickNextButton();

    const firstButtons = getAllByTitle(IDENTIFIERS.TITLE_BUTTON_FIRST);
    firstButtons.forEach(button => {
      const classes = button.className.split(' ');
      expect(classes).not.toContain('button-disabled');
    });
    const backButtons = getAllByTitle(IDENTIFIERS.TITLE_BUTTON_BACK);
    backButtons.forEach(button => {
      const classes = button.className.split(' ');
      expect(classes).not.toContain('button-disabled');
    });
  });

  test('next and last button should be disabled after clicking last button', async () => {
    const { getAllByTitle } = await createThreadList();

    await clickLastButton();

    const firstButtons = getAllByTitle(IDENTIFIERS.TITLE_BUTTON_NEXT);
    firstButtons.forEach(button => {
      const classes = button.className.split(' ');
      expect(classes).toContain('button-disabled');
    });
    const backButtons = getAllByTitle(IDENTIFIERS.TITLE_BUTTON_LAST);
    backButtons.forEach(button => {
      const classes = button.className.split(' ');
      expect(classes).toContain('button-disabled');
    });
  });

  test('clicking on next button should search for threads for next page', async () => {
    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    await createThreadList();

    await clickNextButton();

    const [ url, ..._ ] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    const expectedOffset = 2;
    const expectedLimit = TEST_DATA.PAGE_SIZE;
    const expectedUrl = `${paths.threadApi}?boardId=${TEST_DATA.BOARD_ID}&offset=${expectedOffset}&limit=${expectedLimit}`;
    expect(url).toBe(expectedUrl);
  });

  test('clicking on last button should search for threads for last page', async () => {
    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    await createThreadList();

    await clickLastButton();

    const [ url, ..._ ] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    const expectedOffset = 4;
    const expectedLimit = TEST_DATA.PAGE_SIZE;
    const expectedUrl = `${paths.threadApi}?boardId=${TEST_DATA.BOARD_ID}&offset=${expectedOffset}&limit=${expectedLimit}`;
    expect(url).toBe(expectedUrl);
  });

  test('clicking on back button should search for threads for previous page', async () => {
    await createThreadList();

    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    await createThreadList();

    await clickLastButton();
    await clickBackButton();

    const [ url, ..._ ] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    const expectedOffset = 2;
    const expectedLimit = TEST_DATA.PAGE_SIZE;
    const expectedUrl = `${paths.threadApi}?boardId=${TEST_DATA.BOARD_ID}&offset=${expectedOffset}&limit=${expectedLimit}`;
    expect(url).toBe(expectedUrl);
  });

  test('clicking on first button should search for threads for first page', async () => {
    await createThreadList();

    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    await createThreadList();

    await clickLastButton();
    await clickFirstButton();

    const [ url, ..._ ] = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
    const expectedOffset = 0;
    const expectedLimit = TEST_DATA.PAGE_SIZE;
    const expectedUrl = `${paths.threadApi}?boardId=${TEST_DATA.BOARD_ID}&offset=${expectedOffset}&limit=${expectedLimit}`;
    expect(url).toBe(expectedUrl);
  });
});

// simulate user interaction with ui

const clickFirstButton = async () => {
  return clickButton(IDENTIFIERS.TITLE_BUTTON_FIRST);
};
const clickBackButton = async () => {
  return clickButton(IDENTIFIERS.TITLE_BUTTON_BACK);
};
const clickNextButton = async () => {
  return clickButton(IDENTIFIERS.TITLE_BUTTON_NEXT);
};
const clickLastButton = async () => {
  return clickButton(IDENTIFIERS.TITLE_BUTTON_LAST);
};
const clickButton = async (identifier) => {
  const button = screen.getAllByTitle(identifier)[0];

  await act(async () => {
    button.click();
  });
};
