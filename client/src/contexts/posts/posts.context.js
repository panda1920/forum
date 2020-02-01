import { createContext } from 'react';

const PostsContext = createContext({
    posts: [],
    fetchPosts: () => {},
});

export default PostsContext;