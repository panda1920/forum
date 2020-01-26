import React from 'react';

const Post = (props) => (
  <div className='post'>
    <p>{props.title}</p>
    <p>{props.body}</p>
  </div>
);

export default Post;