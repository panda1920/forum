import React, { useEffect, useState, useCallback } from 'react';

import EntityList from '../../components/entity-list/entity-list.component';
import PostCard from '../../components/post-card/post-card.component';
import { searchPosts } from '../../scripts/api';
import { threadApi } from '../../paths';

const ThreadPage = ({ match, location }) => {
  const { threadId } = match.params;
  const [ thread, setThread ] = useState(null);

  useEffect(() => {
    const hasThreadInState = () => {
      return location.state && location.state.thread;
    };
    const fetchThread = async () => {
      const response = await window.fetch(`${threadApi}/${threadId}`);
      const { threads } = await response.json();
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
    resultJson.entities = resultJson.posts;
    
    return resultJson;
  }, [threadId]);

  const renderChildEntity = (entity, entityNum) => {
    return (
      <PostCard
        key={entity.postId}
        post={entity}
        postnum={entityNum}
      />
    );
  };

  return (
    <div className='thread-page'>
      <div className='breadcrumbs'>
        { thread ? thread.title : null }
        { thread ? thread.ownerBoard[0].title : null }
      </div>
      <EntityList
        searchEntity={searchEntity}
        renderChildEntity={renderChildEntity}
      />
    </div>
  );
};

export default ThreadPage;
