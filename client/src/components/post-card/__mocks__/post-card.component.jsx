import React from 'react';

const mockPostCard = () => {
  return <div />;
};

const PostCard = jest.fn()
  .mockName('Mocked PostCard')
  .mockImplementation(mockPostCard);

export default PostCard;
