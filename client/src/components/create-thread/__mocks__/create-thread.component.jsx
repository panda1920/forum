import React from 'react';

const mockCreateThread = () => {
  return <div className='create-thread' />;
};

const CreateThread = jest.fn()
  .mockName('Mocked CreateThread')
  .mockImplementation(mockCreateThread);

export default CreateThread;
