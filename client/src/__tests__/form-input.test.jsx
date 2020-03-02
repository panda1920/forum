import React from 'react';
import {
  render, screen, cleanup, fireEvent, 
} from '@testing-library/react';

import FormInput from '../components/form-input/form-input.component';

import { setNativeValue } from '../scripts/test-utilities';

afterEach(cleanup);

const TEST_INPUT_ALT = 'This is a test input';

function setupFormInput(onChange, errorMsg) {
  return render(
    <FormInput
      alt={TEST_INPUT_ALT}
      onChange={onChange}
      errorMsg={errorMsg}
      type='text'
    />
  );
}

describe('Testing behavior of form input', () => {
  test('FormInput should render', () => {
    const mock = jest.fn().mockName('mocked onchange handler');
    setupFormInput(mock);
    
    screen.getByAltText(TEST_INPUT_ALT);
  });

  test('change handler should be called when there was input', () => {
    const mock = jest.fn().mockName('mocked onchange handler');
    setupFormInput(mock);
    const input = screen.getByAltText(TEST_INPUT_ALT);

    const event = new Event('input', { bubbles: true });
    setNativeValue(input, 'Hello');
    fireEvent.input(input, event);
    setNativeValue(input, 'World');
    fireEvent.input(input, event);
    setNativeValue(input, '!');
    fireEvent.input(input, event);

    expect(mock.mock.calls.length).toBe(3);
  });

  test('when there is an error message, should render error message', () => {
    const mock = jest.fn().mockName('mocked onchange handler');
    const errorMsg = 'This is some error message';
    setupFormInput(mock, errorMsg);

    screen.getByText(errorMsg);
  });

  test('when there is an error message, should apply error-border class to input', () => {
    const mock = jest.fn().mockName('mocked onchange handler');
    const errorMsg = 'This is some error message';
    setupFormInput(mock, errorMsg);
    const input = screen.getByAltText(TEST_INPUT_ALT);

    const classes = input.getAttribute('class').split(' ');
    expect(classes).toContain('error-border');
  });
});
