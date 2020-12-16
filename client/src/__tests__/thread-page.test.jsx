import React from 'react';
import { render, cleanup, act, screen } from '@testing-library/react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';

import EntityList from '../components/entity-list/entity-list.component';
import PostCard from '../components/post-card/post-card.component';
import CreatePost from '../components/create-post/create-post.component';
import Breadcrumbs from '../components/breadcrumbs/breadcrumbs.component';
import Spinner from '../components/spinner/spinner.component';
import ThreadPage from '../pages/thread/thread-page';

import {
  createMockFetchImplementation,
  createSearchReturn
} from '../scripts/test-utilities';
import {
  searchPosts,
  searchThreads,
  searchBoards,
  viewThread
} from '../scripts/api';
import { clientBoardPath, clientThreadPath } from '../paths';

// mock out child components
jest.mock('../components/entity-list/entity-list.component');
jest.mock('../components/post-card/post-card.component');
jest.mock('../components/htmlinput/htmlinput.component');
jest.mock('../components/breadcrumbs/breadcrumbs.component');
jest.mock('../components/spinner/spinner.component');
jest.mock('../components/create-post/create-post.component');

// mock out api functions
jest.mock('../scripts/api', () => {
  return {
    searchPosts: jest.fn().mockName('mocked searchPosts()'),
    searchThreads: jest.fn().mockName('mocked searchThreads()'),
    searchBoards: jest.fn().mockName('mocked serachBoards()'),
    viewThread: jest.fn().mockName('mocked viewThread()')
  };
});

const TEST_DATA = {
  THREAD_ID: '1',
  THREAD_DATA: {
    threadId: '1',
    userId: 'test_userid',
    boardId: 'test_boardid',
    title: 'test_thread_title',
    createdAt: 1577836800, // 2020/01/01 00:00:00,
    owner: [{
      displayName: 'test_user_name',
    }],
  },
  POSTS_RETURN: [
    { postId: 'test_postid_1' },
    { postId: 'test_postid_2' },
    { postId: 'test_postid_3' },
  ],
  BOARDS_RETURN: [
    { boardId: 'test_boardid', title: 'test_board_title', },
  ],
};

async function renderThreadPage(locations = null) {
  if (!locations)
    locations = [`${clientThreadPath}/${TEST_DATA.THREAD_ID}`];
  let renderResult;
  
  await act(async () => {
    renderResult = render(
      <MemoryRouter
        initialEntries={locations}
      >
        <Switch>
          <Route path={`${clientThreadPath}/:threadId`} component={ThreadPage} />
        </Switch>
      </MemoryRouter>
    );
  });

  return renderResult;
}

beforeEach(() => {
  mockApiFunctions();
});
afterEach(() => {
  cleanup();

  EntityList.mockClear();
  PostCard.mockClear();
  CreatePost.mockClear();
  Breadcrumbs.mockClear();
  Spinner.mockClear();

  searchPosts.mockClear();
  searchThreads.mockClear();
  searchBoards.mockClear();
  viewThread.mockClear();
});

function mockApiFunctions() {
  searchPosts.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn(TEST_DATA.POSTS_RETURN, 'posts')
    ));
  searchThreads.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn([ TEST_DATA.THREAD_DATA ], 'threads')
  ));
  searchBoards.mockImplementation(createMockFetchImplementation(
    true, 200, async () => createSearchReturn(TEST_DATA.BOARDS_RETURN, 'boards')
  ));
}

describe('Testing ThreadPage renders components properly', () => {
  test('Should render EntityList', async () => {
    await renderThreadPage();

    expect(EntityList).toHaveBeenCalledTimes(1);
  });

  test('Should render CreatePost', async () => {
    await renderThreadPage();

    expect(CreatePost).toHaveBeenCalledTimes(1);
  });

  test('Should render Breadcrumbs', async () => {
    await renderThreadPage();

    expect(Breadcrumbs).toHaveBeenCalledTimes(1);
  });

  test('Should render thread info', async () => {
    await renderThreadPage();

    const threadTitle = TEST_DATA.THREAD_DATA.title;
    const threadCreatedAt = '2020/01/01, 00:00:00';
    const threadOwnerName = TEST_DATA.THREAD_DATA.owner[0].displayName;

    expect( screen.getByText(threadTitle, { exact: false }) )
      .toBeInTheDocument();
    expect( screen.getByText(threadCreatedAt, { exact: false }) )
      .toBeInTheDocument();
    expect( screen.getByText(threadOwnerName, { exact: false }) )
      .toBeInTheDocument();
  });

  test('Should render spinner and only spinner when thread fetch fails', async () => {
    searchThreads
      .mockImplementation(createMockFetchImplementation(
        false, 400, async () => {}
      ));

    await renderThreadPage();
    
    expect(Spinner).toHaveBeenCalled();
    expect(EntityList).toHaveBeenCalledTimes(0);
    expect(CreatePost).toHaveBeenCalledTimes(0);
    expect(Breadcrumbs).toHaveBeenCalledTimes(0);
  });

  test('Should render spinner and only spinner when board fetch fails', async () => {
    searchBoards
      .mockImplementation(createMockFetchImplementation(
        false, 400, async () => {}
      ));

    await renderThreadPage();
    
    expect(Spinner).toHaveBeenCalled();
    expect(EntityList).toHaveBeenCalledTimes(0);
    expect(CreatePost).toHaveBeenCalledTimes(0);
    expect(Breadcrumbs).toHaveBeenCalledTimes(0);
  });

  test('Should render components when thread info is in state and fetch was skipped', async () => {
    const locations = [{
      pathname: `/threads/${TEST_DATA.THREAD_ID}`,
      state: { thread: TEST_DATA.THREAD_DATA },
    }];

    await renderThreadPage(locations);

    expect(EntityList).toHaveBeenCalledTimes(1);
    expect(CreatePost).toHaveBeenCalledTimes(1);
    expect(Breadcrumbs).toHaveBeenCalledTimes(1);
  });
});

describe('Testing behavior of ThreadPage', () => {
  test('Should pass callbacks to EntityList', async () => {
    await renderThreadPage();

    for (const call of EntityList.mock.calls) {
      const [ props, ..._ ] = call;

      expect(props).toHaveProperty('searchEntity');
      expect(props).toHaveProperty('renderChildEntity');
      expect(props.searchEntity).toBeInstanceOf(Function);
      expect(props.renderChildEntity).toBeInstanceOf(Function);
    }
  });

  test('Should pass needRefresh to EntityList as false', async () => {
    await renderThreadPage();

    for (const call of EntityList.mock.calls) {
      const [ props, ..._ ] = call;

      expect(props).toHaveProperty('needRefresh', false);
    }
  });

  test('Should search for thread by path id on mount', async () => {
    await renderThreadPage();

    expect(searchThreads).toHaveBeenCalledTimes(1);
    expect(searchThreads).toHaveBeenCalledWith({ threadId: TEST_DATA.THREAD_ID });
  });

  test('Should search for owner board of thread on mount', async () => {
    await renderThreadPage();

    expect(searchBoards).toHaveBeenCalledTimes(1);
    expect(searchBoards).toHaveBeenCalledWith({ boardId: TEST_DATA.THREAD_DATA.boardId });
  });

  test('Should update viewcount of thread on mount', async () => {
    await renderThreadPage();

    expect(viewThread).toHaveBeenCalledTimes(1);
    expect(viewThread).toBeCalledWith(TEST_DATA.THREAD_ID);
  });

  test('Should not search when location state has thread info', async () => {
    const locations = [{
      pathname: `/threads/${TEST_DATA.THREAD_ID}`,
      state: { thread: TEST_DATA.THREAD_DATA },
    }];

    await renderThreadPage(locations);

    expect(searchThreads).not.toHaveBeenCalled();
  });
  
  test('Should pass link definitions to Breadcrumbs', async () => {
    const expectedLink = [
      { displayName: 'Home', path: '/' },
      {
        displayName: TEST_DATA.BOARDS_RETURN[0].title,
        path: `${clientBoardPath}/${TEST_DATA.BOARDS_RETURN[0].boardId}`,
        state: { board: TEST_DATA.BOARDS_RETURN[0] },
      },
      { displayName: TEST_DATA.THREAD_DATA.title, path: null },
    ];

    await renderThreadPage();

    const [ props ] = Breadcrumbs.mock.calls[0];
    const { links } = props;
    expect(links[0]).toMatchObject(expectedLink[0]);
    expect(links[1]).toMatchObject(expectedLink[1]);
    expect(links[2]).toMatchObject(expectedLink[2]);
  });

  test('Should pass threadId to CreatePost', async () => {
    await renderThreadPage();

    for (const call of CreatePost.mock.calls) {
      const [ props, ..._ ] = call;

      expect(props).toHaveProperty('threadId', TEST_DATA.THREAD_ID);
    }
  });

  test('Should pass callback as onCreate to CreatePost', async () => {
    await renderThreadPage();

    for (const call of CreatePost.mock.calls) {
      const [ props, ..._ ] = call;

      expect(props).toHaveProperty('onCreate');
      expect(props.onCreate).toBeInstanceOf(Function);
    }
  });
});

describe('Testing callbacks', () => {
  test('searchEntity callback should search for posts', async () => {
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];

    await act(async () => await searchEntity() );

    expect(searchPosts).toHaveBeenCalledTimes(1);
  });

  test('searchEntity callback should pass options and threadId to searchPosts', async () => {
    const options = { offset: 10, limit: 20 };
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];

    await act(async () => await searchEntity(options) );

    const [ searchOptions ] = searchPosts.mock.calls[0];
    expect(searchOptions)
      .toMatchObject(options);
    expect(searchOptions)
      .toMatchObject({ threadId: TEST_DATA.THREAD_ID });
  });

  test('searchEntity callback should return object with entities field, reference to returned posts', async () => {
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];

    let search;
    await act(async () => {
      search = await searchEntity();
    });

    expect(search).toHaveProperty('result');
    expect(search.result).toHaveProperty('entities', TEST_DATA.POSTS_RETURN);
  });

  test('searchEntity callback should return null when search failed', async () => {
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];
    searchPosts.mockImplementation(createMockFetchImplementation(
      false, 400, async () => {}
    ));

    let search;
    await act(async () => {
      search = await searchEntity({ offset: 10, limit: 20 });
    });

    expect(search).toBeNull();
  });

  test('renderChildEntity callback should render PostCard ', async () => {
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { renderChildEntity } = latestEntityListCall[0];
    cleanup();

    render(
      <div>
        { renderChildEntity(TEST_DATA.POSTS_RETURN[0], 1) }
      </div>
    );

    expect(PostCard).toHaveBeenCalledTimes(1);
    const [ props, ..._ ] = PostCard.mock.calls[0];
    expect(props).toHaveProperty('post', TEST_DATA.POSTS_RETURN[0]);
    expect(props).toHaveProperty('postnum', 1);
  });

  test('onCreate callback should update needRefresh passed to EntityList as true', async () => {
    await renderThreadPage();
    const [ { onCreate } ] = CreatePost.mock.calls.slice(-1)[0];

    await act(async () => { onCreate(); });

    expect(EntityList).toHaveBeenCalledTimes(2);
    const [ props, ..._ ] = EntityList.mock.calls.slice(-1)[0];
    expect(props).toHaveProperty('needRefresh', true);
  });

  test('searchEntity callback should update needRefresh passed to EntityList as false', async () => {
    await renderThreadPage();
    const [ { onCreate } ] = CreatePost.mock.calls.slice(-1)[0];
    const [ { searchEntity } ] = EntityList.mock.calls.slice(-1)[0];

    await act(async () => { onCreate(); });
    await act(async () => { await searchEntity(); });

    expect(EntityList).toHaveBeenCalledTimes(3);
    const [ props, ..._ ] = EntityList.mock.calls.slice(-1)[0];
    expect(props).toHaveProperty('needRefresh', false);
  });
});
