import React from 'react';
import { render, cleanup, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import HtmlInput from '../components/htmlinput/htmlinput.component';
import CreatePost from '../components/create-post/create-post.component';

import { createPost } from '../scripts/api';
import { createMockFetchImplementation } from '../scripts/test-utilities';

// mock out child components
jest.mock('../components/htmlinput/htmlinput.component');

// mock out functions
jest.mock('../scripts/api', () => {
  return {
    createPost: jest.fn().mockName('mocked createPost()')
  };
});

const TEST_DATA = {
  THREAD_ID: 'test_id',
};

function renderCreatePost() {
  const onCreate = jest.fn().mockName('mocked onCreate callback()');
  const renderResult = render(
    <CreatePost threadId={TEST_DATA.THREAD_ID} onCreate={onCreate} />
  );

  return {
    ...renderResult,
    onCreate,
  };
}

beforeEach(() => {
  createPost.mockImplementation(
    createMockFetchImplementation(true, 200, async () => {})
  );
});
afterEach(() => {
  cleanup();
  HtmlInput.mockClear();
  createPost.mockClear();
});
beforeAll(() => {
  jest.useFakeTimers();
});
afterAll(() => {
  jest.useRealTimers();
});

describe('Testing if CreatePost is rendering subcomponents', () => {
  test('Should render CreatePost', () => {
    renderCreatePost();

    expect(HtmlInput).toHaveBeenCalledTimes(1);
  });

  test('Should render Post button', () => {
    const { getByText } = renderCreatePost();

    expect( getByText('Post') ).toBeInTheDocument();
  });
});

describe('Testing behavior of CreatePost', () => {
    test('Should pass text value and callback to htmlInput', () => {
      renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];

      expect(props).toHaveProperty('value');
      expect(props).toHaveProperty('onChange');
      expect(props.value).toBe('');
      expect(props.onChange).toBeInstanceOf(Function);
    });

    test('When post button is pressed error message should show and no API call is fired', async () => {
      const { getByText } = renderCreatePost();
      const postButton = getByText('Post');

      await act(async () => userEvent.click(postButton));

      expect(getByText('Error', { exact: false })).toBeInTheDocument();
      expect(createPost).not.toHaveBeenCalled();
    });

    test('When text is entered before Post button is pressed should fire API call', async () => {
      const { queryByText, getByText} = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      const text = 'lorem ipsum';

      await act(async () => onChangeCallback(text));
      await act(async () => userEvent.click(postButton));

      expect(queryByText('Error', { exact: false })).not.toBeInTheDocument();
      expect(createPost).toHaveBeenCalledTimes(1);
      const [ newPost ] = createPost.mock.calls[0];
      expect(newPost).toMatchObject({
        threadId: TEST_DATA.THREAD_ID,
        content: text,
      });
    });

    test('When <script></script> is entered before Post button is pressed content should be purified', async () => {
      const { getByText } = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      const text = 'hello world<script>alert("hello world")</script>';

      await act(async () => onChangeCallback(text));
      await act(async () => userEvent.click(postButton));

      const [ newPost ] = createPost.mock.calls[0];
      expect(newPost.content).not.toBe(text);
    });

    test('When post is succesful should reset text value', async () => {
      const { getByText } = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      const text = 'lorem ipsum';

      await act(async () => onChangeCallback(text));
      await act(async () => userEvent.click(postButton));

      const [ latestHtmlInputProps ] = HtmlInput.mock.calls.slice(-1)[0];
      expect(latestHtmlInputProps.value).toBe('');
    });

    test('When post is succesful error should disappaer', async () => {
      const { queryByText, getByText } = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      const text = 'lorem ipsum';

      // display error first
      await act(async () => onChangeCallback(''));
      await act(async () => userEvent.click(postButton));
      jest.runAllTimers();
      await act(async () => onChangeCallback(text));
      await act(async () => userEvent.click(postButton));

      expect(queryByText('Error', { exact: false })).not.toBeInTheDocument();
    });

    test('When post was succesful should call prop onCreate', async () => {
      const { getByText, onCreate } = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      const text = 'lorem ipsum';

      await act(async () => onChangeCallback(text));
      await act(async () => userEvent.click(postButton));

      expect(onCreate).toHaveBeenCalledTimes(1);
    });

    test('When post is not succesful should not reset text value and show Error', async () => {
      const { getByText } = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      const text = 'lorem ipsum';
      createPost.mockImplementation(
        createMockFetchImplementation(false, 400, async () => {})
      );

      await act(async () => onChangeCallback(text));
      await act(async () => userEvent.click(postButton));

      const [ latestHtmlInputProps ] = HtmlInput.mock.calls.slice(-1)[0];
      expect(latestHtmlInputProps.value).toBe(text);
      expect(getByText('Error', { exact: false })).toBeInTheDocument();
    });
    
    test('When post is not succesful should not invoke onCreate', async () => {
      const { getByText, onCreate } = renderCreatePost();
      const [ props ] = HtmlInput.mock.calls[0];
      const onChangeCallback = props.onChange;
      const postButton = getByText('Post');
      createPost.mockImplementation(
        createMockFetchImplementation(false, 400, async () => {})
      );

      await act(async () => onChangeCallback('some text'));
      await act(async () => userEvent.click(postButton));

      expect(onCreate).not.toHaveBeenCalled();
    });
});
