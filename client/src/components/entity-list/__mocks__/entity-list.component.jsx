import React from 'react';

const mockEntityList = () => {
  return <div title='EntityList' />;
};

const EntityList = jest.fn()
  .mockName('Mocked EntityList Component')
  .mockImplementation(mockEntityList);

export default EntityList;
