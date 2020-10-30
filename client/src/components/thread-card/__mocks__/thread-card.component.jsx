// this file houses mock implementation of thread-card component
import React from 'react';

const mockThreadCard = () => {
  return <div title='thread card'></div>;
};

const ThreadCard = jest.fn()
  .mockName('Mocked ThreadCard component')
  .mockImplementation(mockThreadCard);

export default ThreadCard;