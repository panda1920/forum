import React from 'react';
import { render, cleanup, act } from '@testing-library/react';

import * as paths from '../paths';
import { createMockFetch } from '../scripts/test-utilities';

import { CurrentUserContext } from '../contexts/current-user/current-user';

import ThreadList from '../components/thread-list/thread-list.component';
import BoardPage from '../pages/board/board-page.component';

// mock out child component
// jest.mock('../components/thread-card/thread-card.component');
jest.mock('../components/thread-list/thread-list.component');

const IDENTIFIERS = {
  TITLE_NAVBAR: 'navigation bar',
  TITLE_HEADING: 'page heading',
  TITLE_BOARDINFO: 'board info',
  TITLE_THREAD_LIST: 'thread list',
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

}

let originalFetch = null;
beforeEach(() => {
  originalFetch = window.fetch;
  window.fetch = createFetchSuccess();
});
afterEach(() => {
  cleanup();
  ThreadList.mockClear();
  window.fetch = originalFetch;
});

describe('testing behavior of board-page', () => {
  test('all subcomponents of board-page should render on screen', async () => {
    const { getByTitle, getAllByTitle } = await createBoardPage();

    expect( getAllByTitle(IDENTIFIERS.TITLE_NAVBAR) )
      .toHaveLength(2);
    getByTitle(IDENTIFIERS.TITLE_HEADING);
    getByTitle(IDENTIFIERS.TITLE_BOARDINFO);
    // expect( getAllByTitle(IDENTIFIERS.TITLE_PAGING) )
    //   .toHaveLength(2);
    getByTitle(IDENTIFIERS.TITLE_THREAD_LIST);
  });

  test('upon render should pass boardId to ThreadList component', async () => {
    await createBoardPage();

    expect(ThreadList).toHaveBeenCalled();
    const [ props, ..._ ] = ThreadList.mock.calls[0];
    expect(props).toHaveProperty('boardId', TEST_DATA.BOARD_ID);
  });
});