import React from 'react';
import { render, cleanup, act } from '@testing-library/react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';

import { threadApi, postApi, createCreateApiPath } from '../paths';
import { createMockFetch } from '../scripts/test-utilities';
import EntityList from '../components/entity-list/entity-list.component';
import PostCard from '../components/post-card/post-card.component';
import HtmlInput from '../components/htmlinput/htmlinput.component';
import ThreadPage from '../pages/thread/thread-page';

// mock out child components
jest.mock('../components/entity-list/entity-list.component');
jest.mock('../components/post-card/post-card.component');
jest.mock('../components/htmlinput/htmlinput.component');

const TEST_DATA = {
  THREAD_ID: '1',
  THREAD_DATA: {
    threadId: '1',
    userId: 'test_userid',
    boardId: 'test_boardid',
    title: 'test_thread_title',
    ownerBoard: [{
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
  window.fetch = originalFetch;
});

describe('Testing ThreadPage renders the component properly', () => {
  test('Should render breadcrumbs', async () => {
    const { getByText } = await renderThreadPage();

    const threadTitlePattern = new RegExp(`.*${TEST_DATA.THREAD_DATA.title}.*`);
    const boardTitlePattern = new RegExp(`.*${TEST_DATA.THREAD_DATA.ownerBoard[0].title}.*`);
    getByText(threadTitlePattern);
    getByText(boardTitlePattern);
  });

  test('Should render EntityList', async () => {
    await renderThreadPage();

    expect(EntityList).toHaveBeenCalled();
  });

  test('Should render HtmlInput', async () => {
    await renderThreadPage();

    expect(HtmlInput).toHaveBeenCalled();
  });

  test.skip('Should render spinner when initial fetch fails', async () => {

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
    
    await searchEntity(options);

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
    
    const { result } = await searchEntity({ offset: 10, limit: 20 });

    expect(result).toHaveProperty('entities', TEST_DATA.POSTS_RETURN);
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
    
    await postEntity(newPostMsg);

    expect(window.fetch).toHaveBeenCalled();
    const [url, options] = window.fetch.mock.calls[0];
    expect(url).toBe(expectedUrl);
    expect(options).toMatchObject(expectedOptions);
    const post = JSON.parse(options.body);
    expect(post).toHaveProperty('content', newPostMsg);
    expect(post).toHaveProperty('threadId', TEST_DATA.THREAD_ID);
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

  test.skip('Should *** if search failed', async () => {

  });

  test.skip('Should *** if search returned no thread', async () => {

  });
});