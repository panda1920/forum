import React, { useState, useEffect } from 'react';

import PostsList from '../../components/postslist/postslist.component';
import HtmlInput from '../../components/htmlinput/htmlinput.component';
import PostsContext from '../../contexts/posts/posts.context';

const PostsPage = () => {
  const [ posts, setPosts ] = useState([]);
  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await fetch('/postlist');
      const { posts } = await response.json();
      setPosts(posts);
    }
    catch (error) {
      console.log('Failed to fetch posts!', error);
    }
  }

  return (
    <div className='postpage'>
      <PostsContext.Provider value={{ posts, fetchPosts }}>
        <PostsList />
        <HtmlInput />
      </PostsContext.Provider>
    </div>
  );
}

export default PostsPage;