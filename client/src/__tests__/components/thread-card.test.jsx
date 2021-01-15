import React from 'react';
import { Router } from 'react-router-dom';
import { render, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryHistory } from 'history';

import ThreadCard from '../../components/thread-card/thread-card.component';

import { clientThreadPath } from '../../paths';

const TEST_DATA = {
  THREAD_DATA: {
    threadId: 'testid',
    userId: 'testuser',
    boardId: 'testboard',
    lastPostId: 'lastpostId',
    title: 'title of thread',
    views: 1234,
    postCount: 22,
    createdAt: 1577836800.1,
    owner: [{
      userId: 'testuser',
      displayName: 'TestUserBobby',
      imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
    }],
    lastPost: [{
      owner: [{
        displayName: 'TEST USER displayName',
        imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
      }],
      createdAt: 1577836830.1,
    }],
  },
  THREAD_CREATED_TIME: '2020/01/01, 00:00:00',
  LASTPOST_CREATED_TIME: '2020/01/01, 00:00:30',
};

const IDENTIFIERS = {
  TITLE_LASTPOST_PORTRAIT: 'last post portrait',
};

function createThreadCard(threadData = null) {
  if (!threadData)
    threadData = TEST_DATA.THREAD_DATA;
  const history = createMemoryHistory();
    
  const renderResult = render(
    <Router
      history={history}
    >
      <ThreadCard thread={threadData} />
    </Router>
  );

  return {
    ...renderResult,
    history
  };
}

beforeEach(() => {

});
afterEach(() => {
  cleanup();
});

describe('Testing behavior of ThreadCard component', () => {
  test('Should render thread information passed as props', () => {
    const { getByText, getByTitle } = createThreadCard();

    getByText(TEST_DATA.THREAD_DATA.title);
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.postCount.toString()}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.views.toString()}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.owner[0].displayName}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_CREATED_TIME}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.LASTPOST_CREATED_TIME}.*`) );
    getByTitle(IDENTIFIERS.TITLE_LASTPOST_PORTRAIT);
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.lastPost[0].owner[0].displayName}.*`) );
  });

  test('Should transition to thread page when clicked on thread title', () => {
    const { getByText, history } = createThreadCard();
    const threadTitle = getByText(TEST_DATA.THREAD_DATA.title);
    const expectedPath = `${clientThreadPath}/${TEST_DATA.THREAD_DATA.threadId}`;

    userEvent.click(threadTitle);

    expect(history.location.pathname).toBe(expectedPath);
  });

  test('Should store thread info in history during transition', () => {
    const { getByText, history } = createThreadCard();
    const threadTitle = getByText(TEST_DATA.THREAD_DATA.title);

    userEvent.click(threadTitle);

    expect(history.location.state).toHaveProperty('thread');
    expect(history.location.state.thread).toMatchObject(TEST_DATA.THREAD_DATA);
  });
});
