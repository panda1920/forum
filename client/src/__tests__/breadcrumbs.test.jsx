import React from 'react';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { render, cleanup, screen, } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import Breadcrumbs from '../components/breadcrumbs/breadcrumbs.component';

const TEST_DATA = {
  DEFAULT_LINKS: [
    { displayName: 'HOME', path: '/' },
    { displayName: 'board1', path: '/board/1' },
    { displayName: 'thread1', path: '/thread/1' },
  ],
  INITIAL_PATH: '/initial',
};

function renderBreadCrumbs(links = undefined) {
  if (links === undefined)
    links = TEST_DATA.DEFAULT_LINKS;
  const history = createMemoryHistory({
    initialEntries: [ TEST_DATA.INITIAL_PATH ],
  });

  const renderResult = render(
    <Router history={history}>
      <Breadcrumbs links={links} />
    </Router>
  );

  return {
    ...renderResult,
    history,
  };
}

beforeEach(() => {

});
afterEach(() => {
  cleanup();
});

describe('Testing Breadcrumbs render things property', () => {
  test('Should render all links', () => {
    renderBreadCrumbs();

    for (const { displayName } of TEST_DATA.DEFAULT_LINKS) {
      expect( screen.getByText(displayName) )
        .toBeInTheDocument();
    }
  });
});

describe('Testing behavior of Breadcrumbs', () => {
  test('Clicking on link should transition to its path', () => {
    const { history } = renderBreadCrumbs();

    expect(history.location.pathname).toBe(TEST_DATA.INITIAL_PATH);

    for (const { displayName, path } of TEST_DATA.DEFAULT_LINKS) {
      const link = screen.getByText(displayName);

      userEvent.click(link);

      expect(history.location.pathname).toBe(path);
    }
  });

  test('Clicking on link with null path should not transition anywhere', () => {
    const links = [
      { displayName: 'someLink', path: '/somelink' },
      { displayName: 'nullLink', path: null },
    ];
    const { history } = renderBreadCrumbs(links);
    const someLink = screen.getByText(links[0].displayName);
    const nullLink = screen.getByText(links[1].displayName);

    expect(history.length).toBe(1);

    userEvent.click(someLink);

    expect(history.length).toBe(2);

    userEvent.click(nullLink);

    expect(history.length).toBe(2);
  });

  test('Clicking on link with state should pass on state information to next location', () => {
    const links = [
      { displayName: 'withstate', path: '/withstate', state: { a: 1, b: 2 } },
      { displayName: 'nostate', path: '/nostate' },
    ];
    const { history } = renderBreadCrumbs(links);
    const withstateLink = screen.getByText(links[0].displayName);
    const nostateLink = screen.getByText(links[1].displayName);

    userEvent.click(nostateLink);

    expect(history.location.state).toBeUndefined();

    userEvent.click(withstateLink);

    expect(history.location.state).toMatchObject(links[0].state);
  });
});
