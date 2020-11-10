import React, { useEffect, useReducer, useContext } from 'react';

import { CurrentUserContext } from '../../contexts/current-user/current-user';
import PaginationBar from '../pagination-bar/pagination-bar.component';

const EntityList = ({ searchEntity, renderChildEntity }) => {
  const [ searchState, dispatch ] = useReducer(reducer, {
    entities: [],
    offset: 0,
    limit: 10,
    totalCount: 0,
  });
  const { setCurrentUser } = useContext(CurrentUserContext);

  // search and store entities everytime offset/limit has changed
  useEffect(() => {
    const searchAndStore = async () => {
      const { result, currentUser } = await searchEntity({
        offset: searchState.offset, limit: searchState.limit,
      });
      dispatch({ type: 'searchResult', result });
      setCurrentUser(currentUser);
    };
    searchAndStore();
  }, [ searchState.offset, searchState.limit, searchEntity, setCurrentUser ]);

  // calculate data passed to pagination
  const displayInfo = {
    firstItemIdx: searchState.offset + 1,
    lastItemIdx: searchState.offset + searchState.entities.length,
    totalCount: searchState.totalCount,
  };

  return (
    <div title='Entity list'>
      <PaginationBar
        displayInfo={displayInfo}
        dispatch={dispatch}
        disableBack={isFirstPage(searchState)}
        disableNext={isLastPage(searchState)}
      />

      {
        searchState.entities.map((entity, idx) => renderChildEntity(entity, idx + 1))
      }

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

// reducer
const reducer = (searchState, action) => {
  switch (action.type) {
    case 'searchResult':
      return {
        ...searchState,
        entities: action.result.entities,
        totalCount: action.result.matchedCount,
      };
    case 'nextPage':
      return {
        ...searchState,
        offset: searchState.offset + searchState.limit,
      };
    case 'lastPage':
      return {
        ...searchState,
        offset: getLastOffset(searchState),
      };
    case 'firstPage':
      return {
        ...searchState,
        offset: 0,
      };
    case 'prevPage':
      return {
        ...searchState,
        offset: searchState.offset - searchState.limit,
      };
    default:
      return searchState;
  }
};

// helpers

function getLastOffset(searchState) {
  const { limit, totalCount } = searchState;
  const entityCountInLastPage = totalCount % limit;
  const pageCount = totalCount / limit;

  if (entityCountInLastPage == 0)
    return (pageCount - 1) * limit;
  else
    return pageCount * limit;
}

function isFirstPage(searchState) {
  return searchState.offset === 0;
}

function isLastPage(searchState) {
  const { offset, limit, totalCount } = searchState;

  return (totalCount - offset) <= limit;
}
