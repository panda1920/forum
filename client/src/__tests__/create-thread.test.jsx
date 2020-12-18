import React from 'react';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { render, cleanup, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import HtmlInput from '../components/htmlinput/htmlinput.component';
import CreateThread from '../components/create-thread/create-thread.component';

import { createThread, createPost } from '../scripts/api';
import { createMockFetchImplementation } from '../scripts/test-utilities';
import { clientBoardPath } from '../paths';

// mock out child components
jest.mock('../components/htmlinput/htmlinput.component');

// mock out functions
jest.mock('../scripts/api', () => {
  return {
    createThread: jest.fn().mockName('mocked createThread()'),
    createPost: jest.fn().mockName('mocked createPost()'),
  };
});

const TEST_DATA = {
  DEFAULT_BOARD_ID: 'test_boardid',
  DEFAULT_NEWTHREAD_ID: 'test_threadid',
  DEFAULT_TITLE_INPUT: 'test_title',
  DEFAULT_POST_INPUT: 'lorem ipsum',
  INITIAL_PATH: '/create-thread',
};

function renderCreateThread() {
  const history = createMemoryHistory({ 
    initialEntries: [ TEST_DATA.INITIAL_PATH ]
  });

  const renderResult = render(
    <Router
      history={history}
    >
      <CreateThread boardId={TEST_DATA.DEFAULT_BOARD_ID} />
    </Router>
  );

  return {
    ...renderResult,
    history,
  };
}

beforeEach(() => {
  createThread.mockImplementation(
    createMockFetchImplementation(true, 200, async () => ({
      result: {
        createdId: TEST_DATA.DEFAULT_NEWTHREAD_ID,
      }
    }))
  );
  createPost.mockImplementation(
    createMockFetchImplementation(true, 200, async () => {})
  );
});
afterEach(() => {
  cleanup();
  HtmlInput.mockClear();
  createThread.mockClear();
  createPost.mockClear();
});
beforeAll(() => {
  jest.useFakeTimers();
});
afterAll(() => {
  jest.useRealTimers();
});

describe('Testing if CreateThread renders subcomponents properly', () => {
  test('Should render HtmlInput', () => {
    renderCreateThread();

    expect(HtmlInput).toHaveBeenCalledTimes(1);
  });
  
  test('Should render input fields', () => {
    const { getByLabelText } = renderCreateThread();

    expect( getByLabelText('Title') ).toBeInTheDocument();
  });

  test('Should render Create button', () => {
    const { getByText } = renderCreateThread();

    expect( getByText('Create') ).toBeInTheDocument();
  });
});

describe('Testing behavior of CreateThread', () => {
  test('Should pass onChange callback to HtmlInput', async () => {
    renderCreateThread();

    for (const call of HtmlInput.mock.calls) {
      const [ props ] = call;

      expect(props).toHaveProperty('onChange');
      expect(props.onChange).toBeInstanceOf(Function);
    }
  });

  test('Should show error message when HtmlInput is invalid and button is clicked', async () => {
    const invalidInputs = [ '', null ];

    for (const invalidInput of invalidInputs) {
      const renderResult = renderCreateThread();
      const { getByText } = renderResult;
      const inputs = { title: TEST_DATA.DEFAULT_TITLE_INPUT, post: invalidInput };
  
      await enterInputAndClickButton(renderResult, inputs);
  
      expect( getByText('Error', { exact: false }) ).toBeInTheDocument();

      cleanup();
    }
  });

  test('Should show error message when Title is invalid and button is clicked', async () => {
    const invalidInputs = [ '', '' ];

    for (const invalidInput of invalidInputs) {
      const renderResult = renderCreateThread();
      const { getByText } = renderResult;
      const inputs = { title: invalidInput, post: TEST_DATA.DEFAULT_POST_INPUT };
  
      await enterInputAndClickButton(renderResult, inputs);

      expect( getByText('Error', { exact: false }) ).toBeInTheDocument();

      cleanup();
    }
  });

  test('Should not fire API calls when input is invalid and button clicked', async () => {
    const invalidInputsPermutation = [
      { title: TEST_DATA.DEFAULT_TITLE_INPUT, post: '' },
      { title: '', post: TEST_DATA.DEFAULT_POST_INPUT },
      { title: '', post: '' },
    ];

    for (const inputs of invalidInputsPermutation) {
      const renderResult = renderCreateThread();

      await enterInputAndClickButton(renderResult, inputs);

      expect(createThread).not.toHaveBeenCalled();
      expect(createPost).not.toHaveBeenCalled();

      cleanup();
    }
  });

  test('Should fire API calls when input is valid and button is clicked', async () => {
    const renderResult = renderCreateThread();
    const inputs = {
      title: TEST_DATA.DEFAULT_TITLE_INPUT,
      post: TEST_DATA.DEFAULT_POST_INPUT,
    };

    await enterInputAndClickButton(renderResult, inputs);

    expect(createThread).toHaveBeenCalledTimes(1);
    expect(createPost).toHaveBeenCalledTimes(1);
    
    const [ newThread ] = createThread.mock.calls[0];
    expect(newThread).toMatchObject({
      boardId: TEST_DATA.DEFAULT_BOARD_ID,
      title: TEST_DATA.DEFAULT_TITLE_INPUT,
    });
    const [ newPost ] = createPost.mock.calls[0];
    expect(newPost).toMatchObject({
      threadId: TEST_DATA.DEFAULT_NEWTHREAD_ID,
      content: TEST_DATA.DEFAULT_POST_INPUT,
    });
  });

  test('Should redirect to board page when API calls is successful', async () => {
      const renderResult = renderCreateThread();
      const { history } = renderResult;
      const inputs = {
        title: TEST_DATA.DEFAULT_TITLE_INPUT,
        post: TEST_DATA.DEFAULT_POST_INPUT,
      };

      await enterInputAndClickButton(renderResult, inputs);

      expect(history.location.pathname)
        .toBe(`${clientBoardPath}/${TEST_DATA.DEFAULT_BOARD_ID}`);
  });

  test('Should show error message when createThread API call fails', async () => {
    const renderResult = renderCreateThread();
    const { getByText } = renderResult;
    const inputs = {
      title: TEST_DATA.DEFAULT_TITLE_INPUT,
      post: TEST_DATA.DEFAULT_POST_INPUT,
    };
    createThread.mockImplementation(
      createMockFetchImplementation(false, 400, () => {})
    );

    await enterInputAndClickButton(renderResult, inputs);

    expect( getByText('Error', { exact: false }) ).toBeInTheDocument();
  });

  test('Should show error message when createPost APi call fails', async () => {
    const renderResult = renderCreateThread();
    const { getByText } = renderResult;
    const inputs = {
      title: TEST_DATA.DEFAULT_TITLE_INPUT,
      post: TEST_DATA.DEFAULT_POST_INPUT,
    };
    createPost.mockImplementation(
      createMockFetchImplementation(false, 400, () => {})
    );

    await enterInputAndClickButton(renderResult, inputs);

    expect( getByText('Error', { exact: false }) ).toBeInTheDocument();
  });

  test('Should not redirect when API calls fails', async () => {
    const renderResult = renderCreateThread();
    const { history } = renderResult;
    const inputs = {
      title: TEST_DATA.DEFAULT_TITLE_INPUT,
      post: TEST_DATA.DEFAULT_POST_INPUT,
    };
    createThread.mockImplementation(
      createMockFetchImplementation(false, 400, () => {})
    );

    await enterInputAndClickButton(renderResult, inputs);

    expect(history.location.pathname).toBe(TEST_DATA.INITIAL_PATH);
  });
});

// helper functions

async function enterInputAndClickButton(renderResult, inputs) {
  const { title, post } = inputs;
  const { getByText, getByLabelText } = renderResult;
  const [ { onChange } ] = HtmlInput.mock.calls.slice(-1)[0];

  // enter title
  await act(async () => {
    userEvent.type(getByLabelText('Title'), title);
  });
  // enter text for new post
  await act(async () => {
    onChange(post);
  });
  // click create button
  await act(async () => {
    userEvent.click(getByText('Create'));
  });
}
