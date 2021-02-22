import React from 'react';
import { render, screen, act, cleanup, } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { updateUserPortrait } from '../../scripts/api';
import { createMockFetchImplementation } from '../../scripts/test-utilities';

jest.mock('../../scripts/api', () => ({
  updateUserPortrait: jest.fn().mockName('mocked updateUserPortrait()'),
}));

function renderProfileFieldPortrait() {
  // TODO
}

describe('Testing that subcomponents are rendered', () => {
  test('Input for file is rendered', () => {

  });

  test('Images are rendered', () => {

  });
});

describe('Testing behavior of ProfileFieldPortrait', () => {
  test('Upload file on the file input should trigger updateUser API call', async () => {

  });

  test('Should refresh current user context when updateUser API call is succesful', () => {

  });

  test('Should not refresh current user context when updatUser API call failed', () => {

  });
});
