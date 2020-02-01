import React, { useState, useContext } from 'react';

import 'tinymce';
import 'tinymce/themes/silver';
import 'tinymce/plugins/help';
import { Editor } from '@tinymce/tinymce-react';

import {
  createInputHandler,
  createPostHandler,
} from './htmlinput.logic';
import PostsContext from '../../contexts/posts/posts.context';

import './htmlinput.style.scss';

const tinymceInitParams = {
  height: 500,
  inline: true,
  menubar: false,
  selector: '.htmlinput-input',
  fixed_toolbar_container: '.htmlinput-menubar',
  skin_url: `${process.env.PUBLIC_URL}/assets/tinymce/skins/ui/oxide`,
  plugins: [
    'help'  
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

const HtmlInput = (props) => {
  const [ content, setContent ] = useState('');
  const { fetchPosts } = useContext(PostsContext);
  const inputHandler = createInputHandler(setContent);
  const postHandler = createPostHandler(content, fetchPosts);

  return (
    <div className='htmlinput'>
      <Editor
        initialValue="<p>This is the initial content of the editor</p>"
        init={tinymceInitParams}
        value={content}
        onEditorChange={inputHandler}
      />
      <div className='htmlinput-menubar'></div>
      <div className='htmlinput-input'></div>
      <button
        className='htmlinput-postbutton'
        name='postbutton'
        onClick={postHandler}
      >
        Post!
      </button>
    </div>
  );
};

export default HtmlInput;