import React, { useState, useCallback } from 'react';

import createDOMPurify from 'dompurify';

import HtmlInput from '../htmlinput/htmlinput.component';
import Button from '../button/button.component';
import ErrorText from '../error-text/error-text.component';

import { createPost } from '../../scripts/api';

import './create-post.styles.scss';

const CreatePost = (props) => {
  const { threadId, onCreate } = props;
  const [ content, setContent ] = useState('');
  const [ error, setError ] = useState(null);

  const post = useCallback(async () => {
    if (!content) {
      setError('Post must not be empty');
      return;
    }
    
    const newPost = { threadId, content: createDOMPurify(window).sanitize(content) };
    const response = await createPost(newPost);
    if (response.ok) {
      setContent('');
      setError(null);
      onCreate();
    }
    else {
      setError('Creation failed');
    }
  }, [ threadId, content, onCreate ]);

  return (
    <div className='create-post'>
      <ErrorText text={error} />
      <HtmlInput
        value={content}
        onChange={setContent}
      />
      <Button className='create-post-button' onClick={post}>
        Post
      </Button>
    </div>
  );
};

export default CreatePost;
