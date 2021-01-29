import React from 'react';

const mockProfileFieldPassword = jest.fn()
  .mockName('mocked ProfileFieldPassword')
  .mockImplementation((props) => {
    const testid = props['data-testid'];

    return <div className='profile-field-text' data-testid={testid} />;
  });


export default mockProfileFieldPassword;
