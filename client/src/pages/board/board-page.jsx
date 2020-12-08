import React, { useEffect, useContext, useState, useCallback } from 'react';

import EntityList from '../../components/entity-list/entity-list.component';
import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import Spinner from '../../components/spinner/spinner.component';
import ThreadCard from '../../components/thread-card/thread-card.component';

import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { searchBoards, searchThreads } from '../../scripts/api';
import { convertEpochToLocalDateString } from '../../scripts/converter';

import './board-page.styles.scss';

const BoardPage = ({ match, location }) => {
  const { boardId } = match.params;
  const [ board, setBoard ] = useState(null);

  // fetch board information from boardId given on mount
  useEffect(() => {
    const isBoardInLocation = location.state && location.state.board;
    const fetchBoardInfo = async () => {
      const response = await searchBoards({ boardId });
      if (!response.ok)
        return;

      const searchJson = await response.json();
      setBoard(searchJson.result.boards[0]);
    };

    if (isBoardInLocation)
      setBoard(location.state.board);
    else
      fetchBoardInfo();
  }, [ boardId, location.state ]);

  // callback passed to EntityList
  const searchEntity = useCallback(async (options) => {
    const searchOptions = Object.assign({ boardId }, options);
    const response = await searchThreads(searchOptions);
    if (!response.ok)
      return null;

    const searchJson = await response.json();
    searchJson.result.entities = searchJson.result.threads;
    return searchJson;
  }, [ boardId ]);

  // callback passed to EntityList
  const renderChildEntity = useCallback((thread, threadnum) => {
    return <ThreadCard key={thread.threadId} thread={thread} threadnum={threadnum} />;
  }, []);

  return renderComponent(board, { searchEntity, renderChildEntity });
};

// render a spinner instead of content when board info is not available
function renderComponent(board, callbacks) {
  if (!board)
  return (
    <Spinner />
  );
    
  const { searchEntity, renderChildEntity } = callbacks;
  const links = [
    { displayName: 'Home', path: '/' },
    { displayName: board.title , path: null },
  ];

  return (
    <div className='board-page' >
      <div className='breadcrumbs-container'>
        <Breadcrumbs
          links={links}
        />
      </div>
      { createBoardInfoSection(board) }
      <EntityList
        searchEntity={searchEntity}
        renderChildEntity={renderChildEntity}
        needRefresh={false}
      />
    </div>
  );
}

function createBoardInfoSection(board){
  const owner = board.owner[0];
  const createdAt = `${owner.displayName} created this board `
  + `at ${convertEpochToLocalDateString(board.createdAt)}`;

  return (
    <div className='board-page-boardinfo'>
      <h1 className='board-title'>{ board.title }</h1>
      <p className='board-createdat'>{ createdAt }</p>
    </div>
  );
}

export default BoardPage;
