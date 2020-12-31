// this file houses mock implementation of UserProfile component
import React from 'react';

const mockUserProfile = () => {
  return <div title='user-profile-page'></div>;
};

const UserProfile = jest.fn()
  .mockName('Mocked UserProfile component')
  .mockImplementation(mockUserProfile);

export default UserProfile;
