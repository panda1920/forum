// this file houses mock implementation of NewThreadPage component
import React from 'react';

const mockNewThreadPage = () => {
  return <div title='newthread-page'></div>;
};

const NewThreadPage = jest.fn()
  .mockName('Mocked NewThreadPage component')
  .mockImplementation(mockNewThreadPage);

export default NewThreadPage;
