import React, { useEffect, useState, useCallback } from 'react';

import { searchPosts, createPost } from '../../scripts/api';
import { threadApi } from '../../paths';
import EntityList from '../../components/entity-list/entity-list.component';
import PostCard from '../../components/post-card/post-card.component';
import HtmlInput from '../../components/htmlinput/htmlinput.component';

import './thread-page.styles.scss';

const ThreadPage = ({ match, location }) => {
  const { threadId } = match.params;
  const [ thread, setThread ] = useState(null);

  useEffect(() => {
    const hasThreadInState = () => {
      return location.state && location.state.thread;
    };
    const fetchThread = async () => {
      const response = await window.fetch(`${threadApi}/${threadId}`);
      const { result: { threads } } = await response.json();
      setThread( threads[0] );
    };

    if (hasThreadInState())
      setThread(location.state.thread);
    else
      fetchThread();
  }, [threadId, location]);

  const searchEntity = useCallback(async (options = {}) => {
    const criteria = Object.assign({ threadId }, options);
    const searchResult = await searchPosts(criteria);
    const resultJson = await searchResult.json();
    resultJson.result.entities = resultJson.result.posts;
    
    return resultJson;
  }, [threadId]);

  const renderChildEntity = useCallback((entity, entityNum) => {
    return (
      <PostCard
        key={entity.postId}
        post={entity}
        postnum={entityNum}
      />
    );
  }, []);

  const postPost = useCallback(async (string) => {
    const newPost = {
      threadId,
      content: string,
    };
    return await createPost(newPost);
  }, [threadId]);

  return (
    <div className='thread-page'>
      <div className='breadcrumbs'>
        { thread ? thread.title : null }
        {
          (thread && thread.ownerBoard)
          ? thread.ownerBoard[0].title
          : null
        }
      </div>
      <EntityList
        searchEntity={searchEntity}
        renderChildEntity={renderChildEntity}
      />
      <HtmlInput
        postEntity={postPost}
      />
    </div>
  );
};

export default ThreadPage;
