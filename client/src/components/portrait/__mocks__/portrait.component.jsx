import React from 'react';

const mockPortrait = () => {
  return <div data-testid='test-portrait'/>;
};

const Portrait = jest.fn()
  .mockName('Mocked portrait()')
  .mockImplementation(mockPortrait);

export default Portrait;
