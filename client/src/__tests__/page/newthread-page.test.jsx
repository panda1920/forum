import React from 'react';
import { Router, Route } from 'react-router-dom';
import { render, cleanup, act } from '@testing-library/react';
import { createMemoryHistory } from 'history';

import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import CreateThread from '../../components/create-thread/create-thread.component';
import Spinner from '../../components/spinner/spinner.component';
import NewThread from '../../pages/newthread/newthread-page';

import { searchBoards } from '../../scripts/api';
import {
  createMockFetchImplementation,
  createSearchReturn,
} from '../../scripts/test-utilities';
import { clientBoardPath } from '../../paths';

// mock out subcomponents
jest.mock('../../components/breadcrumbs/breadcrumbs.component');
jest.mock('../../components/create-thread/create-thread.component');
jest.mock('../../components/spinner/spinner.component');

// mock out functions
jest.mock('../../scripts/api', () => ({
  searchBoards: jest.fn().mockName('mocked searchBoard()'),
}));

const TEST_DATA = {
  BOARD_ID: 'test_boardid',
  BOARD_DATA: {
    boardId: 'test_boardid',
    title: 'board_title',
  },
};

async function renderNewThread(initialLocations) {
  if (!initialLocations)
    initialLocations = ['/'];
  const history = createMemoryHistory({ initialEntries: initialLocations });
  
  let renderResult;

  await act(async () => {
    renderResult = render(
      <Router history={history} >
        <Route
          path='/'
          render={(routeProps) =>
            <NewThread boardId={TEST_DATA.BOARD_ID} {...routeProps} />
          }
        />
      </Router>
    );
  });

  return {
    ...renderResult,
    history,
  };
}

beforeEach(() => {
  searchBoards.mockImplementation(
    createMockFetchImplementation(
      true, 200,
      async () => createSearchReturn([ TEST_DATA.BOARD_DATA ], 'boards'),
    )
  );
});
afterEach(() => {
  cleanup();
  Breadcrumbs.mockClear();
  CreateThread.mockClear();
  Spinner.mockClear();
  searchBoards.mockClear();
});

describe('Testing NewThread to render subcomponents', () => {
  test('Should render Breadcrumbs', async () => {
    await renderNewThread();

    expect(Breadcrumbs).toHaveBeenCalledTimes(1);
  });
  
  test('Should render CreateThread', async () => {
    await renderNewThread();

    expect(CreateThread).toHaveBeenCalledTimes(1);
  });
  
  test('Should render page title', async () => {
    const { getByText } = await renderNewThread();

    expect( getByText(TEST_DATA.BOARD_DATA.title, { exact: false }) )
      .toBeInTheDocument();
    expect( getByText('Create new thread', { exact: false }) )
      .toBeInTheDocument();
  });

  test('Should render Spinner and only Spinner when initial fetch fails', async () => {
    searchBoards.mockImplementation(
      createMockFetchImplementation(false, 400, () => {})
    );

    const { queryByText } = await renderNewThread();

    expect(Spinner).toHaveBeenCalledTimes(1);
    expect(Breadcrumbs).toHaveBeenCalledTimes(0);
    expect(CreateThread).toHaveBeenCalledTimes(0);
    expect( queryByText(TEST_DATA.BOARD_DATA.title, { exact: false }) )
      .not.toBeInTheDocument();
    expect( queryByText('Create new thread', { exact: false } ) )
      .not.toBeInTheDocument();
  });
});

describe('Testing behavior of NewThread', () => {
  test('Should pass boardId to CreateThread', async () => {
    await renderNewThread();

    for (const call of CreateThread.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('boardId', TEST_DATA.BOARD_ID);
    }
  });

  test('Should go fetch board information upon mount', async () => {
    const expectedSearchOptions = {
      boardId: TEST_DATA.BOARD_ID,
    };

    await renderNewThread();

    expect(searchBoards).toHaveBeenCalledTimes(1);
    const [ searchOptions ] = searchBoards.mock.calls[0];
    expect(searchOptions).toMatchObject(expectedSearchOptions);
  });

  test('Should not fetch board information when board state is in history stack', async () => {
    const location = { state: { board: TEST_DATA.BOARD_DATA } };

    await renderNewThread([ location ]);

    expect(searchBoards).toHaveBeenCalledTimes(0);
  });

  test('Should display board title when board state is in history stack', async () => {
    const location = { state: { board: TEST_DATA.BOARD_DATA } };

    const { getByText } = await renderNewThread([ location ]);

    expect( getByText(TEST_DATA.BOARD_DATA.title, { exact: false }) )
      .toBeInTheDocument();
  });

  test('Should pass link definitions to Breadcrumbs', async () => {
    const { boardId, title } = TEST_DATA.BOARD_DATA;
    const expectedLinks = [
      { displayName: 'Home', path: '/' },
      { displayName: title, path: `${clientBoardPath}/${boardId}`},
      { displayName: 'New Thread', path: null },
    ];

    await renderNewThread([ location ]);

    for (const call of Breadcrumbs.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('links');
      expect(props.links).toMatchObject(expectedLinks);
    }
  });
});
