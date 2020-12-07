// this file houses mock implementation of BoardPage component
import React from 'react';

const mockBoardPage = () => {
  return <div title='board-page'></div>;
};

const BoardPage = jest.fn()
  .mockName('Mocked BoardPage component')
  .mockImplementation(mockBoardPage);

export default BoardPage;
