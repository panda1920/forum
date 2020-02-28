import React from 'react';
import {
  render, screen, cleanup, fireEvent, 
} from '@testing-library/react';

import FormInput from '../components/form-input/form-input.component';

afterEach(cleanup);

const TEST_INPUT_ALT = 'This is a test input';

function setupFormInput(onChange) {
  return render(
    <FormInput
      alt={TEST_INPUT_ALT}
      onChange={onChange}
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
});

// helper functions

// sets value on controlled component
// https://stackoverflow.com/questions/40894637/how-to-programmatically-fill-input-elements-built-with-react
function setNativeValue(element, value) {
  const valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
  const prototype = Object.getPrototypeOf(element);
  const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;

  if (valueSetter && valueSetter !== prototypeValueSetter) {
    prototypeValueSetter.call(element, value);
  } else {
    valueSetter.call(element, value);
  }
}