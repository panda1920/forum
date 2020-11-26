import React from 'react';
import { render, cleanup, screen } from '@testing-library/react';

import Portrait from '../components/portrait/portrait.component';
import PostCard from '../components/post-card/post-card.component';
import { createPost } from '../scripts/api';

// mock out child components
jest.mock('../components/portrait/portrait.component');

const TEST_DATA = {
  POST_NUM: 10,
  POST_DATA: {
    postId: '',
    userId: '',
    content: 'Hello there this is test content',
    owner: [{
      displayName: 'test_displayname',
      imageUrl: 'www.example.com/image.png',
    }],
    createdAt: 1605874550, // 2020/11/20, 12:15:50 GMT
  },
};

function createPostCard() {
  return render(
    <PostCard postnum={TEST_DATA.POST_NUM} post={TEST_DATA.POST_DATA} />
  );
}

beforeEach(() => {

});
afterEach(() => {
  cleanup();
  Portrait.mockClear();
});

describe('Testing behavior of PostCard component', () => {
  test('Should render test data passed to component', () => {
    createPostCard();

    const postnum_pattern = new RegExp(`.*${TEST_DATA.POST_NUM}.*`);
    screen.getByText(postnum_pattern);
    screen.getByText(TEST_DATA.POST_DATA.content);
    screen.getByText(TEST_DATA.POST_DATA.owner[0].displayName);
  });

  test('Should pass title and owner user image to portrait', () => {
    createPostCard();

    const passedProps = Portrait.mock.calls[0][0];
    expect(passedProps)
      .toHaveProperty('title');
    expect(passedProps)
      .toHaveProperty('imageUrl', TEST_DATA.POST_DATA.owner[0].imageUrl);
  });

  test('Should display createdtime of post as local time string', () => {
    const expectedString = '2020/11/20, 12:15:50';
    const pattern = new RegExp(`.*${expectedString}.*`);

    createPostCard();

    screen.getByText(pattern);
  });

  test('Should transition to user page when owner portrait is clicked', async () => {

  });

  test('Should transition to user page when owner name is clicked', async () => {

  });
});
