import React from 'react';
import { render, cleanup, act } from '@testing-library/react';

import PaginationBar from '../components/pagination-bar/pagination-bar.component';

const IDENTIFIERS = {
  TITLE_BUTTON_FIRST: 'pagination button first',
  TITLE_BUTTON_BACK: 'pagination button back',
  TITLE_BUTTON_NEXT: 'pagination button next',
  TITLE_BUTTON_LAST: 'pagination button last',
};

const TEST_DATA = {
  DISPLAY_INFO: {
    firstItemIdx: 1,
    lastItemIdx: 3,
    totalCount: 23,
  },
};

function createPaginationBar(disableBack = false, disableNext = false) {
  const mockDispatch = jest.fn().mockName('Mocked dispatch object');
  const renderResult = render(
    <PaginationBar
      displayInfo={TEST_DATA.DISPLAY_INFO}
      disableBack={disableBack}
      disableNext={disableNext}
      dispatch={mockDispatch}
    />
  );

  return {
    ...renderResult,
    mocks: { dispatch: mockDispatch, },
  };
}

beforeEach(() => {
  cleanup();
});

describe('testing behavior of PaginationBar component', () => {
  test('should render all sub components', () => {
    const { getByTitle, getByText } = createPaginationBar();

    getByTitle(IDENTIFIERS.TITLE_BUTTON_FIRST);
    getByTitle(IDENTIFIERS.TITLE_BUTTON_BACK);
    getByTitle(IDENTIFIERS.TITLE_BUTTON_NEXT);
    getByTitle(IDENTIFIERS.TITLE_BUTTON_LAST);
    const expectedDisplayText = `Displaying ${TEST_DATA.DISPLAY_INFO.firstItemIdx}-${TEST_DATA.DISPLAY_INFO.lastItemIdx} of ${TEST_DATA.DISPLAY_INFO.totalCount}`;
    getByText(expectedDisplayText);
  });

  test('back and first buttons should not be disabled when false is passed to disableBack prop', () => {
    const { getByTitle } = createPaginationBar(false, true);

    const first = getByTitle(IDENTIFIERS.TITLE_BUTTON_FIRST);
    const back = getByTitle(IDENTIFIERS.TITLE_BUTTON_BACK);

    expect( first.className.split(' ') ).not.toContain('button-disabled');
    expect( back.className.split(' ') ).not.toContain('button-disabled');
  });

  test('back and first buttons should be disabled when true is passed to disableBack prop', () => {
    const { getByTitle } = createPaginationBar(true, true);

    const first = getByTitle(IDENTIFIERS.TITLE_BUTTON_FIRST);
    const back = getByTitle(IDENTIFIERS.TITLE_BUTTON_BACK);

    expect( first.className.split(' ') ).toContain('button-disabled');
    expect( back.className.split(' ') ).toContain('button-disabled');
  });

  test('next and last buttons should not be disabled when false is passed to disableNext prop', () => {
    const { getByTitle } = createPaginationBar(true, false);

    const next = getByTitle(IDENTIFIERS.TITLE_BUTTON_NEXT);
    const last = getByTitle(IDENTIFIERS.TITLE_BUTTON_LAST);

    expect( next.className.split(' ') ).not.toContain('button-disabled');
    expect( last.className.split(' ') ).not.toContain('button-disabled');
  });

  test('next and last buttons should be disabled when true is passed to disableNext prop', () => {
    const { getByTitle } = createPaginationBar(true, true);

    const next = getByTitle(IDENTIFIERS.TITLE_BUTTON_NEXT);
    const last = getByTitle(IDENTIFIERS.TITLE_BUTTON_LAST);

    expect( next.className.split(' ') ).toContain('button-disabled');
    expect( last.className.split(' ') ).toContain('button-disabled');
  });

  test('clicking on the first button should dispatch firstPage action', () => {
    const { getByTitle, mocks: { dispatch } } = createPaginationBar(false, false);

    act(() => {
      const button = getByTitle(IDENTIFIERS.TITLE_BUTTON_FIRST);
      button.click();
    });

    expect(dispatch).toHaveBeenCalledWith({ type: 'firstPage' });
  });

  test('clicking on the first button should dispatch prevPage action', () => {
    const { getByTitle, mocks: { dispatch } } = createPaginationBar(false, false);

    act(() => {
      const button = getByTitle(IDENTIFIERS.TITLE_BUTTON_BACK);
      button.click();
    });

    expect(dispatch).toHaveBeenCalledWith({ type: 'prevPage' });
  });

  test('clicking on the first button should dispatch nextPage action', () => {
    const { getByTitle, mocks: { dispatch } } = createPaginationBar(false, false);

    act(() => {
      const button = getByTitle(IDENTIFIERS.TITLE_BUTTON_NEXT);
      button.click();
    });

    expect(dispatch).toHaveBeenCalledWith({ type: 'nextPage' });
  });

  test('clicking on the first button should dispatch lastPage action', () => {
    const { getByTitle, mocks: { dispatch } } = createPaginationBar(false, false);

    act(() => {
      const button = getByTitle(IDENTIFIERS.TITLE_BUTTON_LAST);
      button.click();
    });

    expect(dispatch).toHaveBeenCalledWith({ type: 'lastPage' });
  });
});