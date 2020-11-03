import React from 'react';

const mockPortrait = () => {
  return <div></div>;
};

const Portrait = jest.fn()
  .mockName('Mocked portrait')
  .mockImplementation(mockPortrait);

export default Portrait;
