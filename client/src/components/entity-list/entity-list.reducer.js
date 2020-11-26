// This file houses the following:
// reducer for EntityList
// initial state of reducer
// actions that are used for above reducer

const ACTION_TYPES = {
    NEXT_PAGE: 'nextPage',
    LAST_PAGE: 'lastPage',
    PREV_PAGE: 'prevPage',
    FIRST_PAGE: 'firstPage',
    SEARCH_RESULT: 'searchResult',
};

const INITIAL_STATE = {
    entities: [],
    offset: 0,
    limit: 10,
    totalCount: 0,
};

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
          offset: getLastPageOffset(searchState),
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
function getLastPageOffset(searchState) {
    const { limit, totalCount } = searchState;
    const entityCountInLastPage = totalCount % limit;
    const pageNum = Math.floor(totalCount / limit);

    if (entityCountInLastPage == 0)
        return (pageNum - 1) * limit;
    else
        return pageNum * limit;
}

export { reducer, ACTION_TYPES, INITIAL_STATE };
