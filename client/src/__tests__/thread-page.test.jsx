import React from 'react';
import { render, cleanup, act, screen } from '@testing-library/react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';

import { threadApi, postApi, createCreateApiPath } from '../paths';
import { createMockFetch } from '../scripts/test-utilities';
import EntityList from '../components/entity-list/entity-list.component';
import PostCard from '../components/post-card/post-card.component';
import HtmlInput from '../components/htmlinput/htmlinput.component';
import Breadcrumbs from '../components/breadcrumbs/breadcrumbs.component';
import Spinner from '../components/spinner/spinner.component';
import ThreadPage from '../pages/thread/thread-page';

// mock out child components
jest.mock('../components/entity-list/entity-list.component');
jest.mock('../components/post-card/post-card.component');
jest.mock('../components/htmlinput/htmlinput.component');
jest.mock('../components/breadcrumbs/breadcrumbs.component');
jest.mock('../components/spinner/spinner.component');

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
    ownerBoard: [{
      boardId: 'test_boardid',
      title: 'test_board_title',
    }],
  },
  POSTS_RETURN: [
    { postId: 'test_postid_1' },
    { postId: 'test_postid_2' },
    { postId: 'test_postid_3' },
  ],
};

async function renderThreadPage(locations = null) {
  if (!locations)
    locations = [`/threads/${TEST_DATA.THREAD_ID}`];
  let renderResult;
  
  await act(async () => {
    renderResult = render(
      <MemoryRouter
        initialEntries={locations}
      >
        <Switch>
          <Route path='/threads/:threadId' component={ThreadPage} />
        </Switch>
      </MemoryRouter>
    );
  });

  return renderResult;
}

function createApiReturn(entities, entitiesName) {
  return {
    result: {
      [entitiesName]: entities,
      returnCount: entities.length,
      matchedCount: entities.length,
    },
  };
}

let originalFetch = null;
beforeEach(() => {
  originalFetch = window.fetch;
  window.fetch = createMockFetch(true, 200, async () => {
    return createApiReturn([ TEST_DATA.THREAD_DATA ], 'threads');
  });
});
afterEach(() => {
  cleanup();
  EntityList.mockClear();
  PostCard.mockClear();
  HtmlInput.mockClear();
  Breadcrumbs.mockClear();
  Spinner.mockClear();
  window.fetch = originalFetch;
});

describe('Testing ThreadPage renders the component properly', () => {
  test('Should render EntityList', async () => {
    await renderThreadPage();

    expect(EntityList).toHaveBeenCalledTimes(1);
  });

  test('Should render HtmlInput', async () => {
    await renderThreadPage();

    expect(HtmlInput).toHaveBeenCalledTimes(1);
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

  test('Should render spinner and only spinner when initial fetch fails', async () => {
    window.fetch = createMockFetch(false, 400, async () => {});

    await renderThreadPage();

    expect(EntityList).toHaveBeenCalledTimes(0);
    expect(HtmlInput).toHaveBeenCalledTimes(0);
    expect(Breadcrumbs).toHaveBeenCalledTimes(0);
    expect(Spinner).toHaveBeenCalledTimes(1);
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

  test('searchEntity callback should search for posts', async () => {
    // render component and capture component passed to child
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];

    // setup expectation for test case
    window.fetch = createMockFetch(true, 200, async () => {
      return createApiReturn(TEST_DATA.POSTS_RETURN, 'posts');
    });
    const options = { offset: 10, limit: 20 };
    const expectedUrl = `${postApi}?threadId=${TEST_DATA.THREAD_ID}`
      + `&offset=${options.offset}`
      + `&limit=${options.limit}`;
    
    await act(async () => { await searchEntity(options); });

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const [ url, ..._ ] = window.fetch.mock.calls[0];
    expect(url).toBe(expectedUrl);
  });

  test('searchEntity callback should return object with field entities, reference to returned posts', async () => {
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];
    window.fetch = createMockFetch(true, 200, async () => {
      return createApiReturn(TEST_DATA.POSTS_RETURN, 'posts');
    });
    
    let search;
    await act(async () => {
      search = await searchEntity({ offset: 10, limit: 20 });
    });

    expect(search).toHaveProperty('result');
    expect(search.result).toHaveProperty('entities', TEST_DATA.POSTS_RETURN);
  });

  test('searchEntity callback should return null when search failed', async () => {
    await renderThreadPage();
    const latestEntityListCall = EntityList.mock.calls.slice(-1)[0];
    const { searchEntity } = latestEntityListCall[0];
    window.fetch = createMockFetch(false, 400, async () => {});

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

  test('postEntity callback should send create post request to posts api', async () => {
    await renderThreadPage();
    const latestHtmlInputCall = HtmlInput.mock.calls.slice(-1)[0];
    const { postEntity } = latestHtmlInputCall[0];

    window.fetch = createMockFetch(true, 200, async () => {});
    const newPostMsg = 'This is a new post by test test test';
    const expectedUrl = `${createCreateApiPath(postApi)}`;
    const expectedOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
    };
    
    await act(async () => { await postEntity(newPostMsg); });

    expect(window.fetch).toHaveBeenCalled();
    const [url, options] = window.fetch.mock.calls[0];
    expect(url).toBe(expectedUrl);
    expect(options).toMatchObject(expectedOptions);
    const post = JSON.parse(options.body);
    expect(post).toHaveProperty('content', newPostMsg);
    expect(post).toHaveProperty('threadId', TEST_DATA.THREAD_ID);
  });

  test('postEntity callback should update needRefresh passed to EntityList as true', async () => {
    await renderThreadPage();
    const latestHtmlInputCall = HtmlInput.mock.calls.slice(-1)[0];
    const { postEntity } = latestHtmlInputCall[0];

    await act(async () => { await postEntity('some message'); });

    expect(EntityList).toHaveBeenCalledTimes(2);
    const [ props, ..._ ] = EntityList.mock.calls.slice(-1)[0];
    expect(props).toHaveProperty('needRefresh', true);
  });

  test('searchEntity callback should update needRefresh passed to EntityList as false', async () => {
    await renderThreadPage();
    const [ { postEntity } ] = HtmlInput.mock.calls.slice(-1)[0];
    const [ { searchEntity } ] = EntityList.mock.calls.slice(-1)[0];

    await act(async () => { await postEntity('some message'); });
    await act(async () => { await searchEntity(); });

    expect(EntityList).toHaveBeenCalledTimes(3);
    const [ props, ..._ ] = EntityList.mock.calls.slice(-1)[0];
    expect(props).toHaveProperty('needRefresh', false);
  });

  test('Should search for thread with path id on mount', async () => {
    const expectedPath = `${threadApi}/${TEST_DATA.THREAD_DATA.threadId}`;

    await renderThreadPage();

    expect(window.fetch).toHaveBeenCalledTimes(1);
    const [ url, ..._ ] = window.fetch.mock.calls[0];
    expect(url).toBe(expectedPath);
  });

  test('Should not search when location state has thread info', async () => {
    const locations = [{
      pathname: `/threads/${TEST_DATA.THREAD_ID}`,
      state: { thread: TEST_DATA.THREAD_DATA },
    }];

    await renderThreadPage(locations);

    expect(window.fetch).not.toHaveBeenCalled();
  });
  
  test.skip('Should pass link definitions to Breadcrumbs', async () => {
    const expectedLink = [
      { displayName: 'Home', path: '/' },
      {
        displayName: TEST_DATA.THREAD_DATA.ownerBoard[0].title,
        path: `/board/${TEST_DATA.THREAD_DATA.boardId}`
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

  test.skip('Should *** if search failed', async () => {

  });

  test.skip('Should *** if search returned no thread', async () => {

  });
});
