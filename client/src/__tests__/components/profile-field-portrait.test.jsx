import fs from 'fs';

import React from 'react';
import { render, screen, act, } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ProfileFieldPortrait from '../../components/profile-field/profile-field-portrait.component';
import Portrait from '../../components/portrait/portrait.component';
import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { updateUserPortrait } from '../../scripts/api';
import { createMockFetchImplementation } from '../../scripts/test-utilities';

// mock out subcomponents
jest.mock('../../components/portrait/portrait.component');
jest.mock('../../scripts/api', () => ({
  updateUserPortrait: jest.fn().mockName('mocked updateUserPortrait()'),
}));

const TEST_DATA = {
  USER_PROFILE: {
    USER_ID: 'test_id',
  },
  IMAGE_URL: 'example.com/test_image.png',
  FILE: new File(['test data'], 'test_file.text', { type: 'text/plain' }),
};

const IDENTIFIERS = {
  PORTRAIT_ID: 'test-portrait',
};

function renderProfileFieldPortrait() {
  return render(
    <ProfileFieldPortrait imageUrl={TEST_DATA.IMAGE_URL} />
  );
}

beforeEach(() => {
});
afterEach(() => {
  Portrait.mockClear();
  updateUserPortrait.mockClear();
});

describe('Testing that subcomponents are rendered', () => {
  test('Input for file is rendered', () => {
    renderProfileFieldPortrait();

    expect( screen.getByAltText('image-input') )
      .toBeInTheDocument();
  });

  test('Portrait is rendered', () => {
    renderProfileFieldPortrait();

    expect(Portrait).toHaveBeenCalledTimes(1);
    expect( screen.getByTestId(IDENTIFIERS.PORTRAIT_ID) )
      .toBeInTheDocument();
    const [ props ] = Portrait.mock.calls[0];
    expect(props).toHaveProperty('imageUrl', TEST_DATA.IMAGE_URL);
  });
});

describe('Testing behavior of ProfileFieldPortrait', () => {
  test('Update on the file input should trigger update portrait API call', async () => {
    renderProfileFieldPortrait();
    const input = screen.getByAltText('image-input');

    await act(async () => {
      userEvent.upload(input, TEST_DATA.FILE);
    });

    expect(updateUserPortrait).toHaveBeenCalledTimes(1);
    const [ userId, file ] = updateUserPortrait.mock.calls[0];
    expect(userId).toBe(TEST_DATA.USER_PROFILE.USER_ID);
    expect(file).toBe(TEST_DATA.FILE);
  });

  test('Should refresh current user context when update portrait API call is succesful', () => {

  });

  test('Should not refresh current user context when update portrait API call failed', () => {

  });
});
