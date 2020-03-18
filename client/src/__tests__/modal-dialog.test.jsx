import React from 'react';
import ReactModal from 'react-modal';
import {
  render, screen, cleanup, fireEvent, 
} from '@testing-library/react';

import ModalDialog from '../components/modal-dialog/modal-dialog.component';

afterEach(cleanup);
// suppress warnings
ReactModal.setAppElement('*');

const TEST_TITLE = "TEST_MODAL"

function setupModalDialog(toggleOpen) {
  const result = render(
    <div id="root">
      <ModalDialog 
        isOpen={true}
        toggleOpen={toggleOpen}
        title={TEST_TITLE}
      />
    </div>
  );
  ReactModal.setAppElement(result.container);

  return result;
}

function createToggleOpen() {
  return jest.fn().mockName('Mocked toggleOpen()');
}

describe('Testing behavior of modal dialog', () => {
  test('testing that mock is rendered', () => {
    const mockFunction = createToggleOpen();
    setupModalDialog(mockFunction);

    screen.getByTitle(TEST_TITLE);
  });

  test('pressing esc on modal should call toggleOpen()', () => {
    const mockFunction = createToggleOpen();
    setupModalDialog(mockFunction);

    const modal = screen.getByTitle(TEST_TITLE);
    modal.focus();
    // fireEvent(
    //   modal,
    //   new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', charCode: 27, keyCode: 27, bubbles: true })
    // );
    // was stuck here for fucking 2hrs
    // keydown must be used, NOT keyDown **camelCase was the problem
    fireEvent.keyDown(
      modal,
      { key: 'Escape', code: 'Escape', charCode: 27, keyCode: 27 }
    );

    expect(mockFunction.mock.calls.length).toBe(1);
  });

  test('clicking on the close button should call toggleOpen()', () => {
    const mockFunction = createToggleOpen();
    setupModalDialog(mockFunction);

    const close = screen.getByTitle('modal close button');
    close.click();

    expect(mockFunction.mock.calls.length).toBe(1);
  });
});