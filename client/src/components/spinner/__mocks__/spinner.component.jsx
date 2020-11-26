import React from 'react';

const mockSpinner = jest.fn()
  .mockName('Mocked Spinner')
  .mockImplementation(() => (
    <div className='spinner' />
  ));

export default mockSpinner;
