import React from 'react';
import { render, screen, cleanup, act } from '@testing-library/react';

import Button from '../../components/button/button.component';

beforeEach(() => {
  jest.useFakeTimers();
});
afterEach(() => {
  cleanup();
  jest.useRealTimers();
});

describe('testing behavior of Button component', () => {
  test('designated classname should be set on Button', () => {
    const classname = 'dummy_classname';
    setupButton(classname);
    const button = getTestButton();

    const classes = button.getAttribute('class').split(' ');
    
    expect( classes ).toContain(classname);
  });

  test('designated onClick should trigger when Button is clicked',  () => {
    const mockFunction = createMockOnClick();
    setupButton(null, mockFunction);

    expect( mockFunction.mock.calls.length ).toBe(0);

    clickButton();

    expect( mockFunction.mock.calls.length ).toBe(1);
  });

  test('onClick should not trigger twice when two consecutive clicks', () => {
    const mockFunction = createMockOnClick();
    setupButton(null, mockFunction);

    clickButton();
    clickButton();

    expect(mockFunction).toHaveBeenCalledTimes(1);
  });

  test('when there is a wait between clicks onClick should trigger twice', () => {
    const mockFunction = createMockOnClick();
    setupButton(null, mockFunction);

    clickButton();
    act( () => jest.advanceTimersByTime(1000) );
    clickButton();
    
    expect(mockFunction).toHaveBeenCalledTimes(2);
  });
});

// helpers

const TEST_BUTTON_ID = 'test_button';

function setupButton(className, onClick) {
  return (render(
    <Button
      className={className}
      onClick={onClick}
      data-testid={TEST_BUTTON_ID}
    />
  ));
}

function getTestButton() {
  return screen.getByTestId(TEST_BUTTON_ID);
}

function createMockOnClick() {
  return jest.fn().mockName('Mocking onClick()');
}

function clickButton() {
  const button = getTestButton();

  act(() => {
    button.click();
  });
}
