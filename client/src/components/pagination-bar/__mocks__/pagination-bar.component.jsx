import React from 'react';

const mockPaginationBar = () => {
  return (
    <div title='pagination bar' data-testid='test-pagination-bar'>

    </div>
  );
};

const PaginationBar =
  jest.fn()
  .mockName('Mocked PaginationBar Component')
  .mockImplementation(mockPaginationBar);

export default PaginationBar;
