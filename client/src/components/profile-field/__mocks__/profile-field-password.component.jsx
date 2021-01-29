import React from 'react';

const mockProfileFieldPassword = jest.fn()
  .mockName('mocked ProfileFieldPassword')
  .mockImplementation((props) => {
    const testid = props['data-testid'];

    return <div className='profile-field-password' data-testid={testid} />;
  });


export default mockProfileFieldPassword;
