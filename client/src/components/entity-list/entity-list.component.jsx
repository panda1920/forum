import React, { useEffect, useReducer, useContext, useCallback } from 'react';

import { CurrentUserContext } from '../../contexts/current-user/current-user';
import { reducer, INITIAL_STATE, ACTION_TYPES } from './entity-list.reducer';
import PaginationBar from '../pagination-bar/pagination-bar.component';

import './entity-list.styles.scss';

const EntityList = ({ searchEntity, renderChildEntity, needRefresh }) => {
  const [ searchState, dispatch ] = useReducer(reducer, INITIAL_STATE);
  const { setCurrentUser } = useContext(CurrentUserContext);

  // search and store entity in local state
  // triggered when offset or limit changes
  const searchAndStoreEntity = useCallback(async () => {
    const { result, sessionUser } = await searchEntity({
      offset: searchState.offset, limit: searchState.limit,
    });
    dispatch({ type: ACTION_TYPES.SEARCH_RESULT, result });
    setCurrentUser(sessionUser);
  }, [
    searchEntity,
    setCurrentUser,
    searchState.offset,
    searchState.limit
  ]);

  useEffect(() => {
    // console.log('#######First effect!');
    searchAndStoreEntity();
  }, [ searchAndStoreEntity ]);

  // search and store must be triggered
  // when external component notifies that refresh is needed through props
  // this happens independantly from changes to offset or limit
  // which is why a separate useEffect is needed
  useEffect(() => {
    if (needRefresh) {
      // console.log('#######Second effect!');
      searchAndStoreEntity();
    }
  }, [ searchAndStoreEntity, needRefresh ]);

  // calculate data passed to pagination
  const displayInfo = {
    firstItemIdx: searchState.offset + 1,
    lastItemIdx: calculateLastItemIdx(searchState),
    totalCount: searchState.totalCount,
  };

  // console.log('#######Rendering EntityList!');
  // console.log(searchState);
  // console.log(`needRefresh: ${needRefresh}`);

  return (
    <div title='Entity list' className='entity-list'>
      <PaginationBar
        displayInfo={displayInfo}
        dispatch={dispatch}
        disableBack={isFirstPage(searchState)}
        disableNext={isLastPage(searchState)}
      />

      <div className='entity-list-entities'>
        {
          searchState.entities.map(
            (entity, idx) => renderChildEntity(entity, idx + 1 + searchState.offset)
          )
        }
      </div>

      <PaginationBar
        displayInfo={displayInfo}
        dispatch={dispatch}
        disableBack={isFirstPage(searchState)}
        disableNext={isLastPage(searchState)}
      />
    </div>
  );
};

export default EntityList;

// helpers
function isFirstPage(searchState) {
  return searchState.offset === 0;
}

function isLastPage(searchState) {
  const { offset, limit, totalCount } = searchState;

  return (totalCount - offset) <= limit;
}

function calculateLastItemIdx(searchState) {
  if (isLastPage(searchState))
    return searchState.totalCount;
  else
    return searchState.offset + searchState.limit;
}
