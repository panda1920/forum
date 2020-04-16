import React, { useEffect, useContext, useReducer, useCallback } from 'react';

import Button from '../../components/button/button.component';
import BlockText from '../../components/block-text/block-text.component';
import ThreadCard from '../../components/thread-card/thread-card.component';

import { searchThreads } from '../../scripts/api';
import { CurrentUserContext } from '../../contexts/current-user/current-user';

import './thread-list.styles.scss';

const ThreadList = ({ boardId, pageSize }) => {
  const { setCurrentUser } = useContext(CurrentUserContext);
  const [ state, dispatch ] = useReducer(reducer, INITIAL_STATE);

  const firstHandler = useCallback(() => {
    dispatch({ type: 'firstPage' });
  }, [dispatch]);

  const backHandler = useCallback(() => {
    dispatch({ type: 'prevPage' });
  }, [dispatch]);

  const nextHandler = useCallback(() => {
    dispatch({ type: 'nextPage' });
  }, [dispatch]);

  const lastHandler = useCallback(() => {
    dispatch({ type: 'lastPage', pageSize });
  }, [dispatch, pageSize]);

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

  return (
    <div title='thread list' className='thread-list'>
      <div title='pagination' className='pagination'>
        <div className='pagination-space'></div>
        <div className='pagination-text'>
          <BlockText>{generateDisplayRangeText(state, pageSize)}</BlockText>
        </div>
        <div className='pagination-buttons'>
          <Button
            title='pagination button first'
            className={isBackButtonDisabled(state) ? 'button-disabled': ''}
            onClick={firstHandler}
          >
            |&lt;
          </Button>&nbsp;&nbsp;
          <Button
            title='pagination button back'
            className={isBackButtonDisabled(state) ? 'button-disabled': ''}
            onClick={backHandler}
          >
            &lt;
          </Button>&nbsp;&nbsp;&nbsp;&nbsp;
          <Button
            title='pagination button next'
            className={isNextButtonDisabled(state, pageSize) ? 'button-disabled' : ''}
            onClick={nextHandler}
          >
            &gt;
          </Button>&nbsp;&nbsp;
          <Button
            title='pagination button last'
            className={isNextButtonDisabled(state, pageSize) ? 'button-disabled' : ''}
            onClick={lastHandler}
          >
            &gt;|
          </Button>
        </div>
      </div>

      <div title='threads header'></div>
      <div title='threads'>
        {
          state.threads.map(thread => <ThreadCard key={thread.threadId} thread={thread} />)
        }
      </div>

      <div title='pagination' className='pagination'>
        <div className='pagination-space'></div>
        <div className='pagination-text'>
          <BlockText>{generateDisplayRangeText(state, pageSize)}</BlockText>
        </div>
        <div className='pagination-buttons'>
          <Button
            title='pagination button first'
            className={isBackButtonDisabled(state) ? 'button-disabled': ''}
            onClick={firstHandler}
          >
            |&lt;
          </Button>&nbsp;&nbsp;
          <Button
            title='pagination button back'
            className={isBackButtonDisabled(state) ? 'button-disabled': ''}
            onClick={backHandler}
          >
            &lt;
          </Button>&nbsp;&nbsp;&nbsp;&nbsp;
          <Button
            title='pagination button next'
            className={isNextButtonDisabled(state, pageSize) ? 'button-disabled' : ''}
            onClick={nextHandler}
          >
            &gt;
          </Button>&nbsp;&nbsp;
          <Button
            title='pagination button last'
            className={isNextButtonDisabled(state, pageSize) ? 'button-disabled' : ''}
            onClick={lastHandler}
          >
            &gt;|
          </Button>
        </div>
      </div>
    </div>
  );
};

const INITIAL_STATE = {
  threads: [],
  totalThreadCount: 0,
  currentPage: 0,
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
        currentPage: getLastPage(state, action.pageSize),
      };
    default:
      console.log('unknown actiontype in ThreadList');
      return state;
  }
};

const generateDisplayRangeText = (state, pageSize) => {
  const firstItemIdx = pageSize * state.currentPage + 1;
  const lastItemIdx = firstItemIdx + state.threads.length - 1;
  const total = state.totalThreadCount;

  return `Displaying ${firstItemIdx}-${lastItemIdx} of ${total}`;
};

const isBackButtonDisabled = (state) => {
    return state.currentPage === 0;
};

const isNextButtonDisabled = (state, pageSize) => {
  return state.currentPage === getLastPage(state, pageSize);
}

const getLastPage = (state, pageSize) => {
  return Math.ceil( state.totalThreadCount / pageSize ) - 1;
}

export default ThreadList;
