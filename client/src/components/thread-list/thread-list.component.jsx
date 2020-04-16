import React, { useEffect, useContext, useReducer } from 'react';

import ThreadCard from '../../components/thread-card/thread-card.component';
import PaginationBar from '../../components/pagination-bar/pagination-bar.component';

import { searchThreads } from '../../scripts/api';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './thread-list.styles.scss';

const ThreadList = ({ boardId, pageSize }) => {
  const { setCurrentUser } = useContext(CurrentUserContext);
  const [ state, dispatch ] = useReducer(reducer, {
    threads: [],
    totalThreadCount: 0,
    currentPage: 0,
    pageSize
  });

  useEffect(() => {
    let getThreadsInformation = async () => {
      const offset = pageSize * state.currentPage;
      const limit = pageSize;
      const response =  await searchThreads({ boardId, offset, limit });
      if (!response.ok)
        return;
      
      const { result, sessionUser } = await response.json();
      dispatch({ type: 'searchResult', result });
      setCurrentUser(sessionUser);
    };

    getThreadsInformation();
  }, [ boardId, pageSize, setCurrentUser, state.currentPage ]);

  const displayInfo = {
    firstItemIdx: pageSize * state.currentPage + 1,
    lastItemIdx: pageSize * state.currentPage + state.threads.length,
    totalCount: state.totalThreadCount,
  };

  return (
    <div title='thread list' className='thread-list'>
      <PaginationBar
        displayInfo={displayInfo}
        dispatch={dispatch}
        disableBack={isBackButtonDisabled(state)}
        disableNext={isNextButtonDisabled(state, pageSize)}
      />
      <div title='threads header'></div>
      <div title='threads'>
        {
          state.threads.map(thread => <ThreadCard key={thread.threadId} thread={thread} />)
        }
      </div>
      <PaginationBar
        displayInfo={displayInfo}
        dispatch={dispatch}
        disableBack={isBackButtonDisabled(state)}
        disableNext={isNextButtonDisabled(state, pageSize)}
      />
    </div>
  );
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'searchResult':
      return {
        ...state,
        threads: action.result.threads,
        totalThreadCount: action.result.matchedCount,
      };
    case 'firstPage':
      return {
        ...state,
        currentPage: 0,
      };
    case 'prevPage':
      return {
        ...state,
        currentPage: state.currentPage - 1,
      };
    case 'nextPage':
      return {
        ...state,
        currentPage: state.currentPage + 1,
      };
    case 'lastPage':
      return {
        ...state,
        currentPage: getLastPage(state, state.pageSize),
      };
    default:
      console.log('unknown actiontype in ThreadList');
      return state;
  }
};

const isBackButtonDisabled = (state) => {
    return state.currentPage === 0;
};

const isNextButtonDisabled = (state, pageSize) => {
  return state.currentPage === getLastPage(state, pageSize);
};

const getLastPage = (state, pageSize) => {
  return Math.ceil( state.totalThreadCount / pageSize ) - 1;
};

export default ThreadList;
