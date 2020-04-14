import React from 'react';
import { render, cleanup, act } from '@testing-library/react';

import * as paths from '../paths';
import { createMockFetch } from '../scripts/test-utilities';

import { CurrentUserContext } from '../contexts/current-user/current-user';

import ThreadCard from '../components/thread-card/thread-card.component';
import BoardPage from '../pages/board/board-page.component';

// mock out child component
jest.mock('../components/thread-card/thread-card.component');

const IDENTIFIERS = {
  TITLE_NAVBAR: 'navigation bar',
  TITLE_HEADING: 'page heading',
  TITLE_BOARDINFO: 'board info',
  TITLE_PAGING: 'pagination bar',
  TITLE_THREADS: 'threads list',
  TITLE_THREARD_CARD: 'thread card',
};

const TEST_DATA = {
  BOARD_ID: '0',
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
    matchedCount: 2,
  },
};

async function createBoardPage() {
  const mockSetCurrentUser = jest.fn().mockName('Mocked setCurrentUser()');
  let renderResult;

  // needs to wrap render in async act because 
  // board page component is performing asynchronouse state change when mounted
  await act(async () => {
    renderResult = render(
      <CurrentUserContext.Provider
        value={{setCurrentUser: mockSetCurrentUser}}
      >
        <BoardPage boardId={TEST_DATA.BOARD_ID}/>
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

describe('testing behavior of board-page', () => {
  test('all subcomponents of board-page should render on screen', async () => {
    const { getByTitle, getAllByTitle } = await createBoardPage();

    expect( getAllByTitle(IDENTIFIERS.TITLE_NAVBAR) )
      .toHaveLength(2);
    getByTitle(IDENTIFIERS.TITLE_HEADING);
    getByTitle(IDENTIFIERS.TITLE_BOARDINFO);
    expect( getAllByTitle(IDENTIFIERS.TITLE_PAGING) )
      .toHaveLength(2);
    getByTitle(IDENTIFIERS.TITLE_THREADS);
  });

  test('upon rendering should search threads related to this board', async () => {
    const mockFetch = createFetchSuccess();
    window.fetch = mockFetch;
    const expectedEndpoint = paths.threadApi;
    const expectedQuerystring = `?boardId=${TEST_DATA.BOARD_ID}`;
    await createBoardPage();

    expect(mockFetch).toHaveBeenCalled();
    const [ url, options ] = mockFetch.mock.calls[0];
    expect(url).toBe(`${expectedEndpoint}${expectedQuerystring}`);
    expect(options).toMatchObject({
      method: 'GET',
    });
  });

  test('upon rendering should set current user state from return value of api call', async () => {
    const { mocks: { mockSetCurrentUser } } = await createBoardPage();

    expect(mockSetCurrentUser).toHaveBeenCalled();
    const [ userinfo ] = mockSetCurrentUser.mock.calls[0];
    expect(userinfo).toMatchObject(TEST_DATA.API_RETURN_SESSIONUSER);
  });

  test('upon rendering should render threads returned from api as thread cards', async () => {
    const { getAllByTitle } = await createBoardPage();

    const threadCards = getAllByTitle(IDENTIFIERS.TITLE_THREARD_CARD);
    expect(threadCards).toHaveLength(TEST_DATA.API_RETURN_RESULT.threads.length);
    const propsPassed = ThreadCard.mock.calls.map(call => call[0]);
    propsPassed.forEach((prop, idx) => {
      expect(prop).toHaveProperty('thread');
      expect(prop.thread).toMatchObject(TEST_DATA.API_RETURN_RESULT.threads[idx]);
    });
  });
});