import React, { useState, useEffect,  } from 'react';

import Breadcrumbs from '../../components/breadcrumbs/breadcrumbs.component';
import CreateThread from '../../components/create-thread/create-thread.component';
import Spinner from '../../components/spinner/spinner.component';
import BlockText from '../../components/block-text/block-text.component';

import { searchBoards } from '../../scripts/api';
import { clientBoardPath } from '../../paths';

import './newthread-page.styles.scss';

const NewThread = ({ location, boardId }) => {
  const [ board, setBoard ] = useState(null);

  useEffect(() => {
    const isBoardInHistory = location.state && location.state.board;

    const fetchBoard = async () => {
      const response = await searchBoards({ boardId });
      if (!response.ok)
        return;

      const { result: { boards } } = await response.json();
      setBoard(boards[0]);
    };

    if (isBoardInHistory)
      setBoard(location.state.board);
    else
      fetchBoard();
  }, [ boardId, location.state ]);

  if (!board)
    return <Spinner />;

  return (
    <div className='newthread-page'>
      { createBreadcrumbs(board) }
      { createInfoSection(board) }
      <CreateThread boardId={boardId} />
    </div>
  );
};

function createInfoSection(board) {
  return (
    <div className='newthread-page-info'>
      <h1 className='newthread-page-title'>{ 'Create new thread' }</h1>
      <BlockText>{ `Create a new thread for board ${board.title}` }</BlockText>
    </div>
  );
}

function createBreadcrumbs(board) {
  const { boardId, title } = board;
  const links = [
    { displayName: 'Home', path: '/' },
    { displayName: title, path: `${clientBoardPath}/${boardId}`},
    { displayName: 'New Thread', path: null },
  ];

  return (
    <div className='breadcrumbs-container'>
      <Breadcrumbs links={links} />
    </div>
  );
}

export default NewThread;
