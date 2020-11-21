import React, { useState } from 'react';

import 'tinymce';
import 'tinymce/themes/silver';
import 'tinymce/plugins/help';
import { Editor } from '@tinymce/tinymce-react';
import createDOMPurify from 'dompurify';

// import {
//   createInputHandler,
//   createPostHandler,
// } from './htmlinput.logic';
// import PostsContext from '../../contexts/posts/posts.context';

import './htmlinput.style.scss';

const tinymceInitParams = {
  height: 500,
  inline: true,
  menubar: false,
  selector: '.html-input-input',
  fixed_toolbar_container: '.html-input-menubar',
  skin_url: `${process.env.PUBLIC_URL}/assets/tinymce/skins/ui/oxide`,
  plugins: [
    'help',
  ],
  toolbar:
    `undo redo | bold italic underline |
    bullist numlist outdent indent | removeformat | help`,
  init_instance_callback: (editor) => {
    // trick tinymce into thinking that there is focus on editor
    editor.fire('focus');
  },
  setup: (editor) => {
    // by default when focus is lost from editor, toolbar disappears
    // this would suppress that behavior
    editor.on('blur', (event) => {
      return false;
    });
  },
}

const HtmlInput = ({ postEntity }) => {
  const [ content, setContent ] = useState('');
  const inputHandler = (content) => setContent(content);
  const postHandler = async (event) => {
    event.preventDefault();
    const sanitizedContent = createDOMPurify(window).sanitize(content);
    const response = await postEntity(sanitizedContent);
    if (response.ok)
      setContent('');
  };

  return (
    <div className='html-input'>
      <Editor
        initialValue="<p>This is the initial content of the editor</p>"
        init={tinymceInitParams}
        value={content}
        onEditorChange={inputHandler}
      />
      <div className='html-input-menubar'></div>
      <div className='html-input-input'></div>
      <button
        className='html-input-postbutton'
        name='postbutton'
        onClick={postHandler}
      >
        Post!
      </button>
    </div>
  );
};

export default HtmlInput;
