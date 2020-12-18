import React, { useState, useCallback } from 'react';
import { Redirect } from 'react-router-dom';

import ErrorText from '../error-text/error-text.component';
import FormButton from '../form-button/form-button.component';
import HtmlInput from '../htmlinput/htmlinput.component';
import BlockText from '../block-text/block-text.component';
import FormInput from '../form-input/form-input.component';

import { createThread, createPost } from '../../scripts/api';
import { clientBoardPath } from '../../paths';

import './create-thread.styles.scss';

const CreateThread= ({ boardId }) => {
  const [ text, setText ] = useState('');
  const [ title, setTitle ] = useState('');
  const [ error, setError ] = useState('');
  const [ created, setCreated ] = useState(false);

  // usecallback to memoize function
  const validateInput = useCallback((title, text) => {
    if (!title)
      throw 'Title must not be empty.';

    if (!text)
      throw 'Post must not be empty.';
  }, []);

  const clickHandler = useCallback(async () => {
    try {
      validateInput(title, text);

      const newThread = { boardId, title, subject: 'test_subject' };
      let response = await createThread(newThread);
      if (!response.ok)
        throw 'Thread creation failed.';

      let { result: { createdId } } = await response.json();
      const newPost = { threadId: createdId, content: text };
      response = await createPost(newPost);
      if (!response.ok)
        throw 'Post creation failed.';

      setCreated(true);
    }
    catch(error) {
      setError(error);
      return;
    }

  }, [ validateInput, boardId, title, text ]);

  const handleTitleChange = (event) => {
    setTitle(event.target.value);
  };

  if (created)
    return <Redirect to={ `${clientBoardPath}/${boardId}` } />;

  return (
    <div className='create-thread'>
      <form>
        <ErrorText text={error} />

        <BlockText className='create-thread-input-title-label'>
          <label
            htmlFor='create-thread-input-title'
          >
            Title
          </label>
        </BlockText>
        <FormInput
          type='text'
          id='create-thread-input-title'
          className='create-thread-input-title'
          value={title}
          onChange={handleTitleChange}
        />

        <HtmlInput
          value={text}
          onChange={setText}
        />
        
        <FormButton onClick={clickHandler}>Create</FormButton>
      </form>
    </div>
  );
};

export default CreateThread;
