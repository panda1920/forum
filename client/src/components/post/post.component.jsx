import React, { useContext } from 'react';

import TestEntity from '../../components/testentity/testentity.component';

import PostsContext from '../../contexts/posts/posts.context';
import { postApi } from '../../paths';

const Post = (props) => {
  const { postId } = props;
  const { fetchPosts } = useContext(PostsContext);
  return (
    <div className='post'>
      <TestEntity
        entity={{ ...props }}
        apiPath={postApi}
        refresh={fetchPosts}
        id={postId}
      />
    </div>
  );
};

export default Post;