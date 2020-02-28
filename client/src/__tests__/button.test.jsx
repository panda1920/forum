import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';

import Button from '../components/button/button.component';

afterEach(cleanup);

describe('testing behavior of Button component', () => {
  test('designated classname should be set on Button', () => {
    const classname = 'dummy_classname';
    setupButton(classname);
    const button = getTestButton();

    const classes = button.getAttribute('class').split(' ');
    
    expect( classes ).toContain(classname);
  });

  test('designated onClick should trigger when Button is clicked', () => {
    const mockFunction = createMockOnClick();
    setupButton(null, mockFunction);
    const button = getTestButton();

    expect( mockFunction.mock.calls.length ).toBe(0);

    button.click();

    expect( mockFunction.mock.calls.length ).toBe(1);
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