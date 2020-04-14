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
  TIME: '1 1 2020, 00:00PM',
};

const IDENTIFIERS = {
  ALTTEXT_THREAD_PORTRAIT: 'owner portrait',
  ALTTEXT_LASTPOST_PORTRAIT: 'last post portrait',
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
    const { getByText, getByAltText } = createThreadCard();

    getByText(TEST_DATA.THREAD_DATA.title);
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.posts.toString()}.*`) );
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.views.toString()}.*`) );
    getByAltText(IDENTIFIERS.ALTTEXT_THREAD_PORTRAIT);
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.user.displayName}.*`) );
    getByText(/.*1 Jan 2020, 00:00PM.*/);
    getByAltText(IDENTIFIERS.ALTTEXT_LASTPOST_PORTRAIT);
    getByText(/.*1 Jan 2020, 00:30PM.*/);
    getByText( new RegExp(`.*${TEST_DATA.THREAD_DATA.lastPost.user.displayName}.*`) );
  });
});