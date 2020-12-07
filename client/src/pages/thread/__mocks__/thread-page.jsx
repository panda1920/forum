// this file houses mock implementation of ThreadPage component
import React from 'react';

const mockThreadPage = () => {
  return <div title='thread-page'></div>;
};

const ThreadPage = jest.fn()
  .mockName('Mocked ThreadPage component')
  .mockImplementation(mockThreadPage);

export default ThreadPage;
