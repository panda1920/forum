import React from 'react';

const mockBreadcrumbs = jest.fn()
  .mockName('Mocked Breadcrumbs')
  .mockImplementation(() => {
    return (
      <div className='breadcrumbs' />
    );
  });

export default mockBreadcrumbs;
