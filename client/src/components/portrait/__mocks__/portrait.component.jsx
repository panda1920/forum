import React from 'react';

const mockPortrait = () => {
  return <div />;
};

const Portrait = jest.fn()
  .mockName('Mocked portrait')
  .mockImplementation(mockPortrait);

export default Portrait;
