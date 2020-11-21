import React from 'react';
import { render, cleanup, act } from '@testing-library/react';

import { CurrentUserContext } from '../contexts/current-user/current-user';
import PaginationBar from '../components/pagination-bar/pagination-bar.component';
import EntityList from '../components/entity-list/entity-list.component';

// mock out child components
jest.mock('../components/pagination-bar/pagination-bar.component');

const TEST_DATA = {
  SEARCH_RESULT: {
    result: {
      entities: [
        { entityId: 'test_id1' },
        { entityId: 'test_id2' },
        { entityId: 'test_id3' },
        { entityId: 'test_id4' },
        { entityId: 'test_id5' },
        { entityId: 'test_id6' },
        { entityId: 'test_id7' },
        { entityId: 'test_id8' },
        { entityId: 'test_id9' },
        { entityId: 'test_id10' },
      ],
      returnCount: 10,
      matchedCount: 50,
    },
    sessionUser: {
      userId: 'test_userid'
    },
  }
};

async function renderEntityList(mockArguments = {}) {
  let {
    mockSearchEntity,
    mockRenderChildEntity,
    mockSetCurrentUser,
    needRefresh,
    container,
  } = mockArguments;
  
  mockSearchEntity = mockSearchEntity != undefined ? mockSearchEntity :
    jest.fn()
    .mockName('Mocked searchEntity callback')
    .mockImplementation(async () => TEST_DATA.SEARCH_RESULT);
  mockRenderChildEntity = mockRenderChildEntity != undefined ? mockRenderChildEntity :
    jest.fn()
    .mockName('Mocked renderChildEntity callback');
  mockSetCurrentUser = mockSetCurrentUser != undefined ? mockSetCurrentUser :
    jest.fn()
    .mockName('Mocked setCurrentUser');
  needRefresh = needRefresh != undefined ? needRefresh : false;
  const options = { container };
  
  let renderResult;
  await act(async () => {
    renderResult = render(
      <CurrentUserContext.Provider
        value={{ setCurrentUser: mockSetCurrentUser }}
      >
        <EntityList
          searchEntity={mockSearchEntity}
          renderChildEntity={mockRenderChildEntity}
          needRefresh={needRefresh}
        />
      </CurrentUserContext.Provider>
      , options
    );
  });

  return {
    ...renderResult,
    mockSearchEntity,
    mockRenderChildEntity,
    mockSetCurrentUser,
  };
}

beforeEach(() => {

});
afterEach(() => {
  cleanup();
  PaginationBar.mockClear();
});

describe('Testing EntityList is being rendered properly', () => {
  test('Should render 2 PaginationBar', () => {
    renderEntityList();

    expect(PaginationBar).toHaveBeenCalledTimes(2);
  });
});

describe('Testing onmount behavior of EntityList', () => {
  test('Should call searchEntity callback on mount', async () => {
    const expectedOptions = {
      offset: 0,
      limit: 10,
    };

    const { mockSearchEntity } = await renderEntityList();

    expect(mockSearchEntity).toHaveBeenCalledTimes(1);
    const [ passedOptions ] = mockSearchEntity.mock.calls[0];
    expect(passedOptions).toMatchObject(expectedOptions);
  });

  test('Should pass session user returned from search to context', async () => {
    const { mockSetCurrentUser } = await renderEntityList();

    expect(mockSetCurrentUser).toHaveBeenCalledTimes(1);
    const [ passedUser ] = mockSetCurrentUser.mock.calls[0];
    expect(passedUser).toMatchObject(TEST_DATA.SEARCH_RESULT.sessionUser);
  });

  test('Should call render callback for each entity retured from search', async () => {
    const { mockRenderChildEntity } = await renderEntityList();

    expect(mockRenderChildEntity).toHaveBeenCalledTimes(
      TEST_DATA.SEARCH_RESULT.result.entities.length
    );
  });

  test('Should pass entity itself to render callback', async () => {
    const { mockRenderChildEntity } = await renderEntityList();

    mockRenderChildEntity.mock.calls.forEach((call, idx) => {
      const [ passedEntity, num, ..._ ] = call;

      expect(passedEntity).toMatchObject(TEST_DATA.SEARCH_RESULT.result.entities[idx]);
      expect(num).toBe(idx + 1);
    });
  });

  test('Should pass idx of entities displayed to PaginationBar', async () => {
    const expectedDisplayInfo = {
      firstItemIdx: 1,
      lastItemIdx: TEST_DATA.SEARCH_RESULT.result.entities.length,
      totalCount: TEST_DATA.SEARCH_RESULT.result.matchedCount,
    };

    await renderEntityList();

    const latestPaginationBarCalls = PaginationBar.mock.calls.slice(-2);

    for (const call of latestPaginationBarCalls) {
      const [ props, ..._  ] = call;
      expect(props).toHaveProperty('displayInfo');
      expect(props.displayInfo).toMatchObject(expectedDisplayInfo);
    }
  });

  test('Should pass dispatch callback to pagination', async () => {
    await renderEntityList();

    for (const call of PaginationBar.mock.calls) {
      const [ props, ..._  ] = call;
      
      expect(props).toHaveProperty('dispatch');
      expect(props.dispatch).toBeInstanceOf(Function);
    }
  });

  test('Should pass booleans to pagination', async () => {
    await renderEntityList();

    for (const call of PaginationBar.mock.calls) {
      const [ props, ..._  ] = call;
      
      expect(props).toHaveProperty('disableBack');
      expect(props).toHaveProperty('disableNext');
      expect([true, false]).toContain(props.disableBack);
      expect([true, false]).toContain(props.disableNext);
    }
  });

  test('Should trigger search 2 times when needRefresh prop is updated to true', async () => {
    const renderResult = await renderEntityList();
    const { mockSearchEntity } = renderResult;

    expect(mockSearchEntity).toHaveBeenCalledTimes(1);

    // reuse the mock created in the first render and pass it to second
    await renderEntityList({
      ...renderResult,
      needRefresh: true,
    });

    expect(mockSearchEntity).toHaveBeenCalledTimes(2);
  });
});

describe('Testing behavior when dispatch is called', () => {
  test('nextPage should trigger search with updated offset', async () => {
    const expectedOptions = {
      offset: 10,
      limit: 10,
    };
    const { mockSearchEntity } = await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    expect(mockSearchEntity).toHaveBeenCalledTimes(1);

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'nextPage' }) );

    expect(mockSearchEntity).toHaveBeenCalledTimes(2);
    const [ passedOptions ] = mockSearchEntity.mock.calls[1];
    expect(passedOptions).toMatchObject(expectedOptions);
  });

  test('prevPage should trigger search with updated offset', async () => {
    const expectedOptions = {
      offset: 0,
      limit: 10,
    };
    const { mockSearchEntity } = await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    expect(mockSearchEntity).toHaveBeenCalledTimes(1);

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'nextPage' }) );
    await act(async() => dispatch({ type: 'prevPage' }) );

    expect(mockSearchEntity).toHaveBeenCalledTimes(3);
    const [ passedOptions ] = mockSearchEntity.mock.calls[2];
    expect(passedOptions).toMatchObject(expectedOptions);
  });

  test('lastPage should trigger search with updated offset', async () => {
    const expectedOptions = {
      offset: 40,
      limit: 10,
    };
    const { mockSearchEntity } = await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    expect(mockSearchEntity).toHaveBeenCalledTimes(1);

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'lastPage' }) );

    expect(mockSearchEntity).toHaveBeenCalledTimes(2);
    const [ passedOptions ] = mockSearchEntity.mock.calls[1];
    expect(passedOptions).toMatchObject(expectedOptions);
  });

  test('firstPage should trigger search with updated offset', async () => {
    const expectedOptions = {
      offset: 0,
      limit: 10,
    };
    const { mockSearchEntity } = await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    expect(mockSearchEntity).toHaveBeenCalledTimes(1);

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'lastPage' }) );
    await act(async() => dispatch({ type: 'firstPage' }) );

    expect(mockSearchEntity).toHaveBeenCalledTimes(3);
    const [ passedOptions ] = mockSearchEntity.mock.calls[2];
    expect(passedOptions).toMatchObject(expectedOptions);
  });

  test('Should disable pagination next on last page', async () => {
    await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'lastPage' }) );

    const lastPaginationBarCalls = PaginationBar.mock.calls.slice(-2);
    for (const call of lastPaginationBarCalls) {
      const [ props, ..._ ] = call;

      expect(props.disableNext).toBe(true);
      expect(props.disableBack).toBe(false);
    }
  });

  test('Should disable pagination back on first page', async () => {
    await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'lastPage' }) );
    await act(async() => dispatch({ type: 'firstPage' }) );

    const lastPaginationBarCalls = PaginationBar.mock.calls.slice(-2);
    for (const call of lastPaginationBarCalls) {
      const [ props, ..._ ] = call;

      expect(props.disableNext).toBe(false);
      expect(props.disableBack).toBe(true);
    }
  });

  test('Should not disable pagination back or next in the middle page', async () => {
    await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;

    // dispatch triggers async updates; need to wrap with await act()
    await act(async() => dispatch({ type: 'nextPage' }) );

    const lastPaginationBarCalls = PaginationBar.mock.calls.slice(-2);
    for (const call of lastPaginationBarCalls) {
      const [ props, ..._ ] = call;

      expect(props.disableNext).toBe(false);
      expect(props.disableBack).toBe(false);
    }
  });

  test('Should update num passed to renderChildEntity when back/next is dispatched', async () => {
    const { mockRenderChildEntity } = await renderEntityList();
    const dispatch = PaginationBar.mock.calls[0][0].dispatch;
    const getLastCallToRenderEntity = () => mockRenderChildEntity.mock.calls.slice(-1)[0];

    await act(async() => dispatch({ type: 'nextPage' }) );
    let [ _, num ] = getLastCallToRenderEntity();
    expect(num).toBe(TEST_DATA.SEARCH_RESULT.result.entities.length + 10);

    await act(async() => dispatch({ type: 'lastPage' }) );
    [ _, num ] = getLastCallToRenderEntity();
    expect(num).toBe(TEST_DATA.SEARCH_RESULT.result.entities.length + 40);

    await act(async() => dispatch({ type: 'prevPage' }) );
    [ _, num ] = getLastCallToRenderEntity();
    expect(num).toBe(TEST_DATA.SEARCH_RESULT.result.entities.length + 30);

    await act(async() => dispatch({ type: 'firstPage' }) );
    [ _, num ] = getLastCallToRenderEntity();
    expect(num).toBe(TEST_DATA.SEARCH_RESULT.result.entities.length);
  });
});
