import React from 'react';
import { render, cleanup } from '@testing-library/react';

import ThreadCard from '../components/thread-card/thread-card.component';

const TEST_DATA = {
  THREAD_DATA: {
    threadId: 'testid',
    userId: 'testuser',
    boardId: 'testboard',
    lastPostId: 'lastpostId',
    title: 'title of thread',
    views: 1234,
    posts: 22,
    createdAt: 1577836800.1,
    owner: {
      userId: 'testuser',
      displayName: 'TestUserBobby',
      imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
    },
    lastPost: {
      owner: {
        displayName: 'TEST USER displayName',
        imageUrl: 'https://upload.wikimedia.org/wikipedia/en/b/b1/Portrait_placeholder.png',
      },
      createdAt: 1577836830.1,
    }
  },
  THREAD_CREATED_TIME: '01/01/2020, 00:00:00',
  LASTPOST_CREATED_TIME: '01/01/2020, 00:00:30',
};

const IDENTIFIERS = {
  TITLE_LASTPOST_PORTRAIT: 'last post portrait',
};

function createThreadCard() {
  return render(
    <ThreadCard thread={TEST_DATA.THREAD_DATA} />
  );
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
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.posts.toString()}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.views.toString()}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.owner.displayName}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_CREATED_TIME}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.LASTPOST_CREATED_TIME}.*`) );
    getByTitle(IDENTIFIERS.TITLE_LASTPOST_PORTRAIT);
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.lastPost.owner.displayName}.*`) );
  });
});