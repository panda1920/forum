import React from 'react';
import { Router, Switch, Route } from 'react-router-dom';
import { render, cleanup, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryHistory } from 'history';

import EntityList from '../../components/entity-list/entity-list.component';
import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import Spinner from '../../components/spinner/spinner.component';
import ThreadCard from '../../components/thread-card/thread-card.component';
import BoardPage from '../../pages/board/board-page';

import { clientBoardPath } from '../../paths';
import { createMockFetchImplementation, createSearchReturn } from '../../scripts/test-utilities';
import { searchBoards, searchThreads } from '../../scripts/api';

// mock out child component
jest.mock('../../components/entity-list/entity-list.component');
jest.mock('../../components/thread-card/thread-card.component');
jest.mock('../../components/breadcrumbs/breadcrumbs.component');
jest.mock('../../components/spinner/spinner.component');


// mock out dependant functions
jest.mock('../../scripts/api', () => {
  return {
    searchBoards: jest.fn().mockName('mocked searchBoards()'),
    searchThreads: jest.fn().mockName('mocked searchThreads()'),
  };
});

const TEST_DATA = {
  BOARD_ID: 'test_boardid',
  API_RETURN_SESSIONUSER: {
    userId: '1',
    userName: 'testuser@myforumwebapp.com',
  },
  BOARD_DATA: {
    boardId: 'test_boardid',
    userId: 'test_owner_user',
    title: 'test_board_title',
    createdAt: 1577836800, // 2020/01/01 00:00:00,
    owner: [{
      displayName: 'test_user',
    }]
  },
  THREADS_RETURN: [
    { threadId: 'test_thread_id', title: 'test_thread_title' },
    { threadId: 'test_thread_id', title: 'test_thread_title' },
    { threadId: 'test_thread_id', title: 'test_thread_title' },
  ],
};

async function renderBoardPage(locations = null) {
  const mockSetCurrentUser = jest.fn().mockName('Mocked setCurrentUser()');
  if (!locations) locations = createDefaultLocations();
  const history = createMemoryHistory({ initialEntries: locations });

  // needs to wrap render in async act because 
  // board page component is performing asynchronouse state change when mounted
  let renderResult;
  await act(async () => {
    renderResult = render(
      <Router
        history={history}
      >
        <Switch>
          <Route path={`${clientBoardPath}/:boardId`} component={BoardPage}/>
        </Switch>
      </Router>
    );
  });

  return {
    ...renderResult,
    mocks: { mockSetCurrentUser },
    history,
  };
}

function createDefaultLocations() {
  return [
    `${clientBoardPath}/${TEST_DATA.BOARD_ID}`,
  ];
}

beforeEach(() => {
  searchBoards.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn([ TEST_DATA.BOARD_DATA ], 'boards')
  ));
  searchThreads.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn(TEST_DATA.THREADS_RETURN, 'threads')
  ));
});
afterEach(() => {
  cleanup();
  // ThreadList.mockClear();
  EntityList.mockClear();
  Breadcrumbs.mockClear();
  Spinner.mockClear();

  searchBoards.mockClear();
  searchThreads.mockClear();
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

  test('Should render Board info', async () => {
    const { getByText } = await renderBoardPage();

    const titlePattern = new RegExp(`.*${TEST_DATA.BOARD_DATA.title}.*`);
    const ownerPattern = new RegExp(`.*${TEST_DATA.BOARD_DATA.owner[0].displayName}.*`);
    const createdDatePattern = new RegExp(`.*2020/01/01, 00:00:00.*`);

    expect( getByText(titlePattern) ).toBeInTheDocument();
    expect( getByText(ownerPattern) ).toBeInTheDocument();
    expect( getByText(createdDatePattern) ).toBeInTheDocument();
  });

  test('Should render create thread button', async () => {
    const { getByText } = await renderBoardPage();

    expect( getByText('Create thread', { exact: false }) )
      .toBeInTheDocument();
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

    for (const call of EntityList.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('searchEntity');
      expect(props).toHaveProperty('renderChildEntity');
      expect(props.searchEntity).toBeInstanceOf(Function);
      expect(props.renderChildEntity).toBeInstanceOf(Function);
    }
  });

  test('Should pass needRefresh to EntityList as false', async () => {
    await renderBoardPage();

    for (const call of EntityList.mock.calls) {
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

    for (const call of Breadcrumbs.mock.calls) {
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
      { pathname: `${clientBoardPath}/${TEST_DATA.BOARD_ID}`, state: { board: TEST_DATA.BOARD_DATA } },
    ];

    await renderBoardPage(locations);

    expect(searchBoards).not.toHaveBeenCalled();
  });

  test('Should transition to CreateThread when create thread button is clicked', async () => {
    const { getByText, history } =await renderBoardPage();
    const createThreadButton = getByText('Create thread', { exact: false });
    const expectedPath = `${clientBoardPath}/${TEST_DATA.BOARD_ID}/new`;

    await act(async () => userEvent.click(createThreadButton) );

    expect(history.location.pathname).toBe(expectedPath);
  });

  test('Should pass board information as state when create thread button is clicked', async () => {
    const { getByText, history } =await renderBoardPage();
    const createThreadButton = getByText('Create thread', { exact: false });
    const expectedState = { board: TEST_DATA.BOARD_DATA };

    await act(async () => userEvent.click(createThreadButton) );

    expect(history.location.state).toMatchObject(expectedState);
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
    expect(result.result).toHaveProperty('entities', TEST_DATA.THREADS_RETURN);
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
