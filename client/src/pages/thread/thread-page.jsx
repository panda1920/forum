import React, { useEffect, useState, useCallback } from 'react';

import { searchPosts, createPost } from '../../scripts/api';
import { threadApi } from '../../paths';
import { convertEpochToLocalDateString } from '../../scripts/converter';
import EntityList from '../../components/entity-list/entity-list.component';
import PostCard from '../../components/post-card/post-card.component';
import HtmlInput from '../../components/htmlinput/htmlinput.component';
import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import Spinner from '../../components/spinner/spinner.component';

import './thread-page.styles.scss';

const ThreadPage = ({ match, location }) => {
  const { threadId } = match.params;
  const [ thread, setThread ] = useState(null);
  const [ needRefresh, setNeedRefresh ] = useState(false);

  useEffect(() => {
    const hasThreadInState = () => location.state && location.state.thread;
    const fetchThread = async () => {
      const response = await window.fetch(`${threadApi}/${threadId}`);
      if (!response.ok)
        return;

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
    const response = await searchPosts(criteria);
    if (!response.ok)
      return null;

    const resultJson = await response.json();
    resultJson.result.entities = resultJson.result.posts;

    setNeedRefresh(false);
    
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
    const result = await createPost(newPost);

    if (result.ok) setNeedRefresh(true);

    return result;
  }, [threadId]);

  // console.log('#######Rendering ThreadPage!');

  return createThreadPage(thread, needRefresh, {
    searchEntity,
    renderChildEntity,
    postPost,
  });
};

function createThreadPage(thread, needRefresh, callbacks) {
  const { searchEntity, renderChildEntity, postPost } = callbacks;

  // wanted to avoid rendering the page when thread info is not available
  if (!thread)
    return (
      <Spinner />
    );

  return (
    <div className='thread-page'>
      { createBreadcrumbs(thread) }
      { createThreadInfoSection(thread) }
      <EntityList
        searchEntity={searchEntity}
        renderChildEntity={renderChildEntity}
        needRefresh={needRefresh}
      />
      <HtmlInput postEntity={postPost} />
    </div>
  );
}

function createBreadcrumbs(thread) {
  // create navigation links to other pages
  // const ownerBoard = thread.ownerBoard[0];
  const links = [
    { displayName: 'Home', path: '/' },
    // { displayName: ownerBoard.title, path: `/board/${ownerBoard.boardId}` },
    { displayName: thread.title, path: null },
  ];

  return (
    <div className='breadcrumbs-container'>
      <Breadcrumbs links={links} />
    </div>
  );
}

function createThreadInfoSection(thread) {
  const owner = thread.owner[0];
  const createdBy = `${owner.displayName} created this thread `
    + `at ${convertEpochToLocalDateString(thread.createdAt)}`;

  return (
    <div className='thread-page-threadinfo'>
      <h1 className='thread-title'>{ thread.title }</h1>
      <p className='thread-creation'>{ createdBy }</p>
    </div>
  );
}

export default ThreadPage;
