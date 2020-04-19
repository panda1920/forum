# -*- coding: utf-8 -*-
"""
This file houses test code for search_service.py
"""
import pytest

from server.services.search_service import SearchService

import tests.mocks as mocks

MOCKAGGREGATE_RETURN_OR = 'or'
MOCKAGGREGATE_RETURN_AND = 'and'


@pytest.fixture(scope='function')
def service():
    mockDB = mocks.createMockDB()
    mockFilter = mocks.createMockFilter()
    mockAggregate = mocks.createMockAggregateFilter()
    mockAggregate.createFilter.side_effect = lambda x, y: x
    mockPaging = mocks.createMockPaging()
    yield SearchService(mockDB, mockFilter, mockAggregate, mockPaging)


class TestSearchUsersByKeyValues:
    MOCKDB_DEFAULT_RETURN = dict(
        users=[ dict(userId=0, _id='11223344'), dict(userId=1, _id='11223345') ],
        returnCount=2,
        matchedCount=2,
    )
    MOCKFILTER_DEFAULT_RETURN = 'default_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'
    DEFAULT_KEYVALUES = dict(search='username1')

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        service._repo.searchUser.return_value = self.MOCKDB_DEFAULT_RETURN
        service._filter.createFilter.return_value = self.MOCKFILTER_DEFAULT_RETURN
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchUsersByKeyValuesConvertsSearchTermToFilters(self, service):
        mockFilter = service._filter

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_any_call({
            'field': 'userName',
            'operator': 'fuzzy',
            'value': [ 'username1' ]
        })
        mockFilter.createFilter.assert_any_call({
            'field': 'displayName',
            'operator': 'fuzzy',
            'value': [ 'username1' ]
        })

    def test_searchUsersConvertMultipleSearchKeys(self, service):
        mockFilter = service._filter
        keyValues = dict(search='username1 username2')

        service.searchUsersByKeyValues(keyValues)

        mockFilter.createFilter.assert_any_call({
            'field': 'userName',
            'operator': 'fuzzy',
            'value': [ 'username1', 'username2' ]
        })
        mockFilter.createFilter.assert_any_call({
            'field': 'displayName',
            'operator': 'fuzzy',
            'value': [ 'username1', 'username2' ]
        })

    def test_searchUsersShouldConvertUserIdToEqFilter(self, service):
        mockFilter = service._filter
        userIdToSearch = '11223344'
        keyValues = dict(userId=userIdToSearch)

        service.searchUsersByKeyValues(keyValues)

        mockFilter.createFilter.assert_any_call({
            'field': 'userId',
            'operator': 'eq',
            'value': [ userIdToSearch ]
        })

    def test_searchUsersPassesFiltersToAggregate(self, service):
        mockAggregate = service._aggregate

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockAggregate.createFilter.assert_any_call(
            'or',
            [ self.MOCKFILTER_DEFAULT_RETURN, self.MOCKFILTER_DEFAULT_RETURN ]
        )

    def test_searchUserByKeyValuesPassesKeyValuessToPaging(self, service):
        mockPaging = service._paging
        
        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_searchUsersByKeyValuesQueriesCrudWithCreatedPagingAndFilter(self, service):
        mockDB = service._repo

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockDB.searchUser.assert_called_with(
            MOCKAGGREGATE_RETURN_AND,
            paging=self.MOCKPAGING_DEFAULT_RETURN
        )

    def test_searchUsersByKeyValuesReturnsNoUsersWhenNoSearchTermInKeyValues(self, service):
        keyValues = dict(offset=30, limit=500)

        searchResult = service.searchUsersByKeyValues(keyValues)

        assert searchResult == dict(
            users=[],
            returnCount=0,
            matchedCount=0
        )

    def test_searchUsersByKeyValuesReturnFilteredReturnUsersFromQuery(self, service):
        # MOCKDB_DEFAULT_RETURN = dict(
        #     users=[ dict(userId=0, _id='11223344'), dict(userId=1, _id='11223345') ],
        #     returnCount=2,
        #     matchedCount=2,
        # )
        expectedResult = dict(
            users=[ dict(userId=0), dict(userId=1) ],
            returnCount=2,
            matchedCount=2,
        )
        
        searchResult = service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        assert searchResult == expectedResult


class TestSearchPostsByKeyValues:
    MOCKDB_DEFAULT_RETURN = dict(
        posts=[ dict(postId='2222', userId='11111111', _id='some_random_id') ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKDB_USER_DEFAULT_RETURN = dict(
        users=[ dict(userId='11111111', name='Alan', _id='some_random_id')],
        returnCount=1,
        matchedCount=1,
    )
    MOCKFILTER_DEFAULT_RETURN = 'default_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'
    DEFAULT_KEYVALUE = dict(search='some_content')

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        service._repo.searchPost.return_value = self.MOCKDB_DEFAULT_RETURN
        service._repo.searchUser.return_value = self.MOCKDB_USER_DEFAULT_RETURN
        service._filter.createFilter.return_value = self.MOCKFILTER_DEFAULT_RETURN
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchPostsByKeyValuesConvertsSearchTermToFuzzyFilter(self, service):
        mockFilter = service._filter

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockFilter.createFilter.assert_any_call(dict(
            field='content',
            operator='fuzzy',
            value=[ self.DEFAULT_KEYVALUE['search'] ]
        ))

    def test_searchPostByKeyValuesConvertsCertainKeysToEqFilter(self, service):
        mockFilter = service._filter
        fieldNameAgainstValuesList = [
            dict(fieldname=['threadId'], value=['11223344']),
            dict(fieldname=['userId'], value=['99999999']),
            dict(fieldname=['createdAt'], value=[11113333]),
            dict(fieldname=['threadId', 'createdAt'], value=['11223344', 11113333]),
        ]

        for fieldNameAgainstValues in fieldNameAgainstValuesList:
            mockFilter.reset_mock()
            keyValue = {}
            for fieldname, value in zip(fieldNameAgainstValues['fieldname'], fieldNameAgainstValues['value']):
                keyValue[fieldname] = value
            
            service.searchPostsByKeyValues(keyValue)

            for fieldname, value in zip(fieldNameAgainstValues['fieldname'], fieldNameAgainstValues['value']):
                mockFilter.createFilter.assert_any_call(dict(
                    field=fieldname,
                    operator='eq',
                    value=[value]
                ))

    def test_searchPostsByKeyValuesPassesFiltersToAggregate(self, service):
        mockAggregate = service._aggregate

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockAggregate.createFilter.assert_any_call('or', [ self.MOCKFILTER_DEFAULT_RETURN ])

    def test_searchPostsByKeyValuesPassesKeyValueToPaging(self, service):
        mockPaging = service._paging

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUE)

    def test_searchPostsByKeyValuesWithNoSearchTermReturnsNoMatch(self, service):
        keyValues = dict(
            offset=30, limit=100
        )

        searchResult = service.searchPostsByKeyValues(keyValues)
        assert searchResult == dict(
            posts=[],
            returnCount=0,
            matchedCount=0,
        )

    def test_searchPostsByKeyValuesPassesCreatedFilterAndPagingToQuery(self, service):
        mockDB = service._repo

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockDB.searchPost.assert_any_call(
            MOCKAGGREGATE_RETURN_AND,
            paging=self.MOCKPAGING_DEFAULT_RETURN
        )

    def test_searchPostsByKeyValuesCreatesEQFilterFromUserId(self, service):
        mockFilter = service._filter

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockFilter.createFilter.assert_any_call(dict(
            field='userId',
            operator='eq',
            value=[ self.MOCKDB_DEFAULT_RETURN['posts'][0]['userId'] ]
        ))

    def test_searchPostsByKeyValuesCreatesEQFilterFromMultiplePosts(self, service):
        mockDB = service._repo
        mockDB.searchPost.return_value = dict(
            posts=[ dict(userId='11111111'), dict(userId='22222222') ],
            returnCount=2,
            matchedCount=2,
        )
        mockFilter = service._filter

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockFilter.createFilter.assert_any_call(dict(
            field='userId',
            operator='eq',
            value=[ '11111111', '22222222' ]
        ))

    def test_searchPostsByKeyValuesQueriesUserByCreatedFilter(self, service):
        mockDB = service._repo

        service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        mockDB.searchUser.assert_called_with(
            self.MOCKFILTER_DEFAULT_RETURN
        )

    def test_searchPostByKeyValuesReturnFilteredReturnFromBothQueries(self, service):
        expectedResult = dict(
            posts=[
                dict(
                    postId='2222',
                    userId='11111111',
                    owner=dict(userId='11111111', name='Alan'),
                )
            ],
            returnCount=1,
            matchedCount=1,
        )

        searchResult = service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        assert searchResult == expectedResult


class TestSearchThreadByKeyValues:
    DEFAULT_KEYVALUES = dict(
        userId='test_id',
        search='test_search',
    )
    MOCKDB_DEFAULT_RETURN = dict(
        threads=[ dict(threadId='2222', userId='11111111', _id='some_random_id', lastPostId='1234') ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKDB_USER_DEFAULT_RETURN = dict(
        users=[
            dict(userId='11111111', name='Alan', _id='some_random_id'),
            dict(userId='33333333', name='Bobby', _id='some_random_id'),
        ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKDB_POST_DEFAULT_RETURN = dict(
        posts=[ dict(postId='1234', userId='33333333') ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKFILTER_DEFAULT_RETURN = 'default_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        service._repo.searchThread.return_value = self.MOCKDB_DEFAULT_RETURN
        service._repo.searchUser.return_value = self.MOCKDB_USER_DEFAULT_RETURN
        service._repo.searchPost.return_value = self.MOCKDB_POST_DEFAULT_RETURN
        service._filter.createFilter.return_value = self.MOCKFILTER_DEFAULT_RETURN
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchThreadsByKeyValuesShouldCreateFuzzyFilterForFields(self, service):
        mockFilter = service._filter

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_any_call(dict(
            field='subject',
            operator='fuzzy',
            value=[ self.DEFAULT_KEYVALUES['search'] ],
        ))
        mockFilter.createFilter.assert_any_call(dict(
            field='title',
            operator='fuzzy',
            value=[ self.DEFAULT_KEYVALUES['search'] ],
        ))
    
    def test_searchThreadsByKeyValuesShouldCreateEqFilterForId(self, service):
        mockFilter = service._filter

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_any_call(dict(
            field='userId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['userId'] ],
        ))

    def test_searchThreadsByKeyValuesShouldGenerateAggregate(self, service):
        mockAggregate = service._aggregate

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockAggregate.createFilter.assert_any_call(
            'or',
            [ self.MOCKFILTER_DEFAULT_RETURN, self.MOCKFILTER_DEFAULT_RETURN ]
        )
        mockAggregate.createFilter.assert_any_call(
            'and',
            [ self.MOCKFILTER_DEFAULT_RETURN, MOCKAGGREGATE_RETURN_OR ]
        )

    def test_searchThreadsByKeyValuesShouldPassKeyValuesToPaging(self, service):
        mockPaging = service._paging

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_searchThreadsByKeyValuesShouldCallRepoWithAndFilter(self, service):
        mockRepo = service._repo

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockRepo.searchThread.assert_called_with(
            MOCKAGGREGATE_RETURN_AND,
            paging=self.MOCKPAGING_DEFAULT_RETURN
        )

    def test_searchThreadsByKeyValuesShouldNotUpdateThreadViewCount(self, service):
        mockRepo = service._repo

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        # _, update = mockRepo.updateThread.call_args[0]
        assert mockRepo.updateThread.call_count == 0

    def test_searchThreadsByKeyValuesShouldNotCallRepoWhenNothingToSearchFor(self, service):
        mockRepo = service._repo
        keyValues = dict(offset=30, limit=100)

        service.searchThreadsByKeyValues(keyValues)

        assert mockRepo.searchThread.call_count == 0
        assert mockRepo.updateThread.call_count == 0

    def test_searchThreadsByKeyValuesShouldGenerateSearchForOwnerUser(self, service):
        mockFilter = service._filter
        mockRepo = service._repo

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_any_call(dict(
            field='userId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['userId'] ],
        ))
        mockFilter.createFilter.assert_any_call(dict(
            field='userId',
            operator='eq',
            value=[ self.MOCKDB_POST_DEFAULT_RETURN['posts'][0]['userId'] ],
        ))
        mockRepo.searchUser.assert_any_call(
            self.MOCKFILTER_DEFAULT_RETURN
        )

    def test_searchThreadsByKeyValuesShouldGenerateSearchForLastPost(self, service):
        mockFilter = service._filter

        service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_any_call(dict(
            field='postId',
            operator='eq',
            value=[ self.MOCKDB_DEFAULT_RETURN['threads'][0]['lastPostId'] ],
        ))

    def test_searchThreadsByKeyValuesShouldReturnSearchResult(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        assert result['returnCount'] == self.MOCKDB_DEFAULT_RETURN['returnCount']
        assert result['matchedCount'] == self.MOCKDB_DEFAULT_RETURN['matchedCount']
        threads = result['threads']
        assert len(threads) == len(self.MOCKDB_DEFAULT_RETURN['threads'])
        assert threads[0]['threadId'] == self.MOCKDB_DEFAULT_RETURN['threads'][0]['threadId']

    def test_searchThreadsByKeyValuesShouldReturnNoMatchWhenNothingToSearchFor(self, service):
        keyValues = dict(offset=30, limit=100)

        result = service.searchThreadsByKeyValues(keyValues)

        assert len(result['threads']) == 0
        assert result['returnCount'] == 0
        assert result['matchedCount'] == 0

    def test_searchThreadsByKeyValuesShouldContainOwnerInfo(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        threads = result['threads']
        for thread in threads:
            assert 'owner' in thread

    def test_searchThreadsByKeyValuesShouldContainLastPostInfo(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        threads = result['threads']
        for thread in threads:
            assert 'lastPost' in thread
            assert 'owner' in thread['lastPost']

    def test_searchThreadsByKeyValuesShouldFilterFieldsFromResult(self, service):
        result = service.searchThreadsByKeyValues(self.DEFAULT_KEYVALUES)

        threads = result['threads']
        owners = [
            thread['owner'] for thread in threads
        ]
        lastPosts = [
            thread['lastPost'] for thread in threads
        ]
        for thread in threads:
            assert '_id' not in thread
        for owner in owners:
            assert '_id' not in owner
        for lastPost in lastPosts:
            assert '_id' not in lastPost
            assert '_id' not in lastPost['owner']


class TestSaerchThreadByExplicitId:
    DEFAULT_THREAD_ID = 'test_id'
    MOCKDB_DEFAULT_RETURN = dict(
        threads=[ dict(threadId='test_id', userId='11111111', _id='some_random_id') ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKDB_USER_DEFAULT_RETURN = dict(
        users=[ dict(userId='11111111', name='Alan', _id='some_random_id')],
        returnCount=1,
        matchedCount=1,
    )
    MOCKFILTER_DEFAULT_RETURN = 'default_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        service._repo.searchThread.return_value = self.MOCKDB_DEFAULT_RETURN
        service._repo.searchUser.return_value = self.MOCKDB_USER_DEFAULT_RETURN
        service._filter.createFilter.return_value = self.MOCKFILTER_DEFAULT_RETURN
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchThreadByExplicitIdShouldCreateEqFilterForId(self, service):
        mockFilter = service._filter

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        mockFilter.createFilter.assert_any_call(dict(
            field='threadId',
            operator='eq',
            value=[ self.DEFAULT_THREAD_ID ],
        ))

    def test_searchThreadByExplicitIdShouldGenerateAggregate(self, service):
        mockAggregate = service._aggregate

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        mockAggregate.createFilter.assert_any_call(
            'and',
            [ self.MOCKFILTER_DEFAULT_RETURN ]
        )

    def test_searchThreadByExplicitIdShouldCallRepoWithAndFilter(self, service):
        mockRepo = service._repo

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        mockRepo.searchThread.assert_called_with(
            MOCKAGGREGATE_RETURN_AND,
            paging=self.MOCKPAGING_DEFAULT_RETURN
        )

    def test_searchThreadByExplicitIdShouldUpdateThreadViewCount(self, service):
        mockRepo = service._repo
        expectedUpdate = dict(increment='views')

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert mockRepo.updateThread.call_count == 1
        _, update = mockRepo.updateThread.call_args[0]
        assert update == expectedUpdate

    def test_searchThreadByExplicitIdShouldGenerateSearchForOwnerUser(self, service):
        mockFilter = service._filter
        mockRepo = service._repo

        service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        mockFilter.createFilter.assert_any_call(dict(
            field='userId',
            operator='eq',
            value=[ self.MOCKDB_DEFAULT_RETURN['threads'][0]['userId'] ],
        ))
        mockRepo.searchUser.assert_any_call(
            self.MOCKFILTER_DEFAULT_RETURN
        )

    def test_searchThreadByExplicitIdShouldReturnSearchResult(self, service):
        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        assert result['returnCount'] == self.MOCKDB_DEFAULT_RETURN['returnCount']
        assert result['matchedCount'] == self.MOCKDB_DEFAULT_RETURN['matchedCount']
        threads = result['threads']
        assert len(threads) == len(self.MOCKDB_DEFAULT_RETURN['threads'])
        assert threads[0]['threadId'] == self.MOCKDB_DEFAULT_RETURN['threads'][0]['threadId']

    def test_searchThreadByExplicitIdShouldContainOwnerInfo(self, service):
        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        threads = result['threads']
        for thread in threads:
            assert 'owner' in thread

    def test_searchThreadByExplicitIdShouldFilterFieldsFromResult(self, service):
        result = service.searchThreadByExplicitId(self.DEFAULT_THREAD_ID)

        threads = result['threads']
        owners = [
            thread['owner'] for thread in threads
        ]
        for thread in threads:
            assert '_id' not in thread
        for owner in owners:
            assert '_id' not in owner
