import React, { useContext } from 'react';

import Post from '../../components/post/post.component';

import PostsContext from '../../contexts/posts/posts.context';

const PostsList = () => {
  const { posts } = useContext(PostsContext);
  return (
    <div className='postslist'>
      {
        posts.map(post => {
          return <Post key={post.postId} {...post} />
        })
      }
    </div>
  );
}

export default PostsList;