import React from 'react';

const mockCreatePost = () => {
  return <div />;
};

const CreatePost = jest.fn()
  .mockName('Mocked CreatePost')
  .mockImplementation(mockCreatePost);

export default CreatePost;
