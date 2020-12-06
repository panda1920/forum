import React from 'react';
import { render, cleanup, act } from '@testing-library/react';

import * as paths from '../paths';
import { createMockFetch, createMockFetchImplementation, createSearchReturn } from '../scripts/test-utilities';
import { searchBoards, searchThreads } from '../scripts/api';

import { CurrentUserContext } from '../contexts/current-user/current-user';

import ThreadList from '../components/thread-list/thread-list.component';
import EntityList from '../components/entity-list/entity-list.component';
import Breadcrumbs from '../components/breadcrumbs/breadcrumbs.component';
import Spinner from '../components/spinner/spinner.component';
import ThreadCard from '../components/thread-card/thread-card.component';
import BoardPage from '../pages/board/board-page.component';

// mock out child component
// jest.mock('../components/thread-card/thread-card.component');
jest.mock('../components/thread-list/thread-list.component');

// mock out dependant functions
jest.mock('../scripts/api', () => {
  return {
    searchBoards: jest.fn().mockName('mocked searchBoards()'),
    searchThreads: jest.fn().mockName('mocked searchThreads()'),
  };
});

const IDENTIFIERS = {
  TITLE_NAVBAR: 'navigation bar',
  TITLE_HEADING: 'page heading',
  TITLE_BOARDINFO: 'board info',
  TITLE_THREAD_LIST: 'thread list',
};

const TEST_DATA = {
  BOARD_ID: 'test_boardid',
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
  BOARD_DATA: {
    boardId: 'test_boardid',
    userId: 'test_owner_user',
    title: 'test_board_title',
    createdAt: 1577836800, // 2020/01/01 00:00:00,
  },
  THREADS_RETURN: [
    { threadId: 'test_thread_id', title: 'test_thread_title' },
    { threadId: 'test_thread_id', title: 'test_thread_title' },
    { threadId: 'test_thread_id', title: 'test_thread_title' },
  ],
};

async function renderBoardPage() {
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
  searchBoards.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn([ TEST_DATA.BOARD_DATA ], 'boards')
  ));
  searchThreads.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn(TEST_DATA.THREADS_RETURN, 'threads')
  ));
});
afterEach(() => {
  cleanup();
  ThreadList.mockClear();
  window.fetch = originalFetch;
  searchBoards.mockClear();
  searchThreads.mockClear();
});

describe('testing behavior of board-page', () => {
  test('all subcomponents of board-page should render on screen', async () => {
    const { getByTitle, getAllByTitle } = await renderBoardPage();

    expect( getAllByTitle(IDENTIFIERS.TITLE_NAVBAR) )
      .toHaveLength(2);
    getByTitle(IDENTIFIERS.TITLE_HEADING);
    getByTitle(IDENTIFIERS.TITLE_BOARDINFO);
    // expect( getAllByTitle(IDENTIFIERS.TITLE_PAGING) )
    //   .toHaveLength(2);
    getByTitle(IDENTIFIERS.TITLE_THREAD_LIST);
  });

  test('upon render should pass boardId to ThreadList component', async () => {
    await renderBoardPage();

    expect(ThreadList).toHaveBeenCalled();
    const [ props, ..._ ] = ThreadList.mock.calls[0];
    expect(props).toHaveProperty('boardId', TEST_DATA.BOARD_ID);
  });
});

describe('Testing BoardPage renders the components properly', () => {
  test('Should render EntityList', async () => {
    await renderBoardPage();

    expect(EntityList).toHaveBeenCalledTimes(1);
  });

  test('Should render BreadCrumbs', async () => {
    await renderBoardPage();

    expect(Breadcrumbs).toHaveBeenCalledTimes(1);
  });

  test.skip('Should render Board info', async () => {

  });

  test('Should render Spinner and only Spinner when board fetch fails', async () => {
    searchBoards.mockImplementation(createMockFetchImplementation(
      false, 400, async () => {}
    ));

    await renderBoardPage();

    expect(Spinner).toHaveBeenCalled();
    expect(EntityList).toHaveBeenCalledTimes(0);
    expect(Breadcrumbs).toHaveBeenCalledTimes(0);
  });
});

describe('Testing behavior of BoardPage', () => {
  test('Should pass callbacks to EntityList', async () => {
    await renderBoardPage();

    for (const call in EntityList.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('searchEntity');
      expect(props).toHaveProperty('renderEntity');
      expect(props.searchEntity).toBeInstanceOf(Function);
      expect(props.renderEntity).toBeInstanceOf(Function);
    }
  });

  test('Should pass needRefresh to EntityList as false', async () => {
    await renderBoardPage();

    for (const call in EntityList.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('needRefresh', false);
    }
  });
  
  test('Should pass link definitions to Breadcrumbs', async () => {
    const expectedLinks = [
      { displayName: 'Home', path: '/' },
      { displayName: TEST_DATA.BOARD_DATA.title , path: null },
    ];

    await renderBoardPage();

    for (const call in Breadcrumbs.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('links');
      const { links } = props;
      expect(links[0]).toMatchObject(expectedLinks[0]);
      expect(links[1]).toMatchObject(expectedLinks[1]);
    }
  });

  test('Should search board info by path id on mount', async () => {
    await renderBoardPage();

    expect(searchBoards).toHaveBeenCalledTimes(1);
    expect(searchBoards).toHaveBeenCalledWith({ boardId: TEST_DATA.BOARD_ID });
  });

  test('Should not search board info when location state has board info', async () => {
    const locations = [
      { pathname: `/boards/${TEST_DATA.BOARD_ID}`, state: { board: TEST_DATA.BOARD_DATA } },
    ];

    await renderBoardPage(locations);

    expect(searchBoards).not.toHaveBeenCalled();
  });
});

describe('Testing callbacks of BoardPage', () => {
  test('searchEntity callback should search for threads', async () => {
    await renderBoardPage();
    const [ EntityListProps ] = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = EntityListProps;

    await act(async () => await searchEntity() );

    expect(searchThreads).toHaveBeenCalledTimes(1);
  });

  test('searchEntity callback should pass options and boardId to searchThreads', async () => {
    const options = { offset: 10, limit: 50 };
    await renderBoardPage();
    const [ EntityListProps ] = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = EntityListProps;

    await act(async () => await searchEntity(options) );

    const [ searchOptions ] = searchThreads.mock.calls[0];
    expect(searchOptions).toMatchObject(options);
    expect(searchOptions).toMatchObject({ boardId: TEST_DATA.BOARD_ID });
  });

  test('searchEntity callback should return object with entities field, reference to returned threads', async () => {
    await renderBoardPage();
    const [ EntityListProps ] = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = EntityListProps;

    let result;
    await act(async () => {
      result = await searchEntity();
    });

    expect(result).toHaveProperty('result');
    expect(result.result).toHaveProperty('threads', TEST_DATA.THREADS_RETURN);
  });

  test('searchEntity callback should return null when search failed', async () => {
    searchThreads.mockImplementation(createMockFetchImplementation(
      false, 400, async () => {}
    ));
    await renderBoardPage();
    const [ EntityListProps ] = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = EntityListProps;

    let result;
    await act(async () => {
      result = await searchEntity();
    });

    expect(result).toBeNull();
  });

  test('renderChildEntity callback should render ThreadCard ', async () => {
    await renderBoardPage();
    const [ EntityListProps ] = EntityList.mock.calls.slice(-1)[0];
    const { renderChildEntity } = EntityListProps;
    cleanup();

    render(
      <div>
        { renderChildEntity(TEST_DATA.THREADS_RETURN[0], 1) }
      </div>
    );

    expect(ThreadCard).toHaveBeenCalledTimes(1);
    const [ props ] = ThreadCard.mock.calls[0];
    expect(props).toHaveProperty('thread', TEST_DATA.THREADS_RETURN[0]);
    expect(props).toHaveProperty('threadnum', 1);
  });
});
