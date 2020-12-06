import React, { useEffect, useState, useCallback } from 'react';

import { searchPosts, createPost, searchThreadById, searchBoards } from '../../scripts/api';
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
  const [ board, setBoard ] = useState(null);
  const [ needRefresh, setNeedRefresh ] = useState(false);

  // initlal fetch thread info from id
  useEffect(() => {
    const hasThreadInState = () => location.state && location.state.thread;
    const fetchThread = async () => {
      const response = await searchThreadById(threadId);
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

  // fetch initial board info from fetched thread
  useEffect(() => {
    const fetchOwnerBoard = async () => {
      const response = await searchBoards({ boardId : thread.boardId });
      if (!response.ok)
        return;

      const { result: { boards } } = await response.json();
      setBoard( boards[0] );
    };

    if (thread)
      fetchOwnerBoard();
  }, [thread]);

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

  return createThreadPage(thread, board, needRefresh, {
    searchEntity,
    renderChildEntity,
    postPost,
  });
};

function createThreadPage(thread, board, needRefresh, callbacks) {
  const { searchEntity, renderChildEntity, postPost } = callbacks;

  // wanted to avoid rendering the page when thread info is not available
  const isEntityAvailable = thread && board;
  if (!isEntityAvailable)
    return (
      <Spinner />
    );

  return (
    <div className='thread-page'>
      { createBreadcrumbs(thread, board) }
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

function createBreadcrumbs(thread, board) {
  // create navigation links to other pages
  const links = [
    { displayName: 'Home', path: '/' },
    { displayName: board.title, path: `/board/${board.boardId}` },
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
