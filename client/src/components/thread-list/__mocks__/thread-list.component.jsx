import React from 'react';

const mockThreadList = () => {
  return (
    <div title='thread list'>

    </div>
  );
};

const ThreadList =
  jest.fn()
  .mockName('mocked ThreadList component')
  .mockImplementation(mockThreadList);

export default ThreadList;
