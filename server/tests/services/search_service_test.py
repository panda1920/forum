# -*- coding: utf-8 -*-
"""
This file houses test code for search_service.py
"""
import pytest

from server.services.search_service import SearchService

import tests.mocks as mocks
import server.app_utils as app_utils

@pytest.fixture(scope='function')
def service():
    mockDB= mocks.createMockDB()
    mockFilter = mocks.createMockFilter()
    mockPaging = mocks.createMockPaging()
    yield SearchService(mockDB, mockFilter, mockPaging)

class TestSearchUsersByKeyValues:
    MOCKDB_DEFAULT_RETURN = dict(
        users=[ 'user1', 'user2'],
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

    def test_searchUsersByKeyValuesConvertsSearchTermToFuzzyFilterForUsername(self, service):
        mockFilter = service._filter

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_called_with({
            'field': 'userName',
            'operator': 'fuzzy',
            'value': [ 'username1' ]
        })

    def test_searchUsersConvertMultipleSearchKeys(self, service):
        mockFilter = service._filter
        keyValues = dict(search='username1 username2')

        service.searchUsersByKeyValues(keyValues)

        mockFilter.createFilter.assert_called_with({
            'field': 'userName',
            'operator': 'fuzzy',
            'value': [ 'username1', 'username2' ]
        })

    def test_searchUserByKeyValuesPassesKeyValuessToPaging(self, service):
        mockPaging = service._paging
        
        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_searchUsersByKeyValuesQueriesCrudWithCreatedPagingAndFilter(self, service):
        mockDB= service._repo

        service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        mockDB.searchUser.assert_called_with(
            [ self.MOCKFILTER_DEFAULT_RETURN ],
            self.MOCKPAGING_DEFAULT_RETURN
        )

    def test_searchUsersByKeyValuesReturnsNoUsersWhenNoSearchTermInKeyValues(self, service):
        mockDB = service._repo
        keyValues = dict(offset=30, limit=500)

        searchResult = service.searchUsersByKeyValues(keyValues)

        assert searchResult == dict(
            users=[],
            returnCount=0,
            matchedCount=0
        )

    def test_searchUsersByKeyValuesReturnWhatsReturnedFromQuery(self, service):
        mockDB = service._repo

        searchResult = service.searchUsersByKeyValues(self.DEFAULT_KEYVALUES)

        assert searchResult == self.MOCKDB_DEFAULT_RETURN

class TestSearchUserById:
    MOCKDB_DEFAULT_RETURN = dict(
        users=[ 'user1' ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKFILTER_DEFAULT_RETURN = 'default_filter'
    MOCKPAGING_DEFAULT_RETURN = 'default_paging'
    DEFAULT_ID = '11111111'
    DEFAULT_KEYVALUE = dict(offset=20, limit=100)

    @pytest.fixture(scope='function', autouse=True)
    def setDefaultReturnValues(self, service):
        service._repo.searchUser.return_value = self.MOCKDB_DEFAULT_RETURN
        service._filter.createFilter.return_value = self.MOCKFILTER_DEFAULT_RETURN
        service._paging.return_value = self.MOCKPAGING_DEFAULT_RETURN

    def test_searchUsersByIdConvertsIdToEqFilter(self, service):
        mockFilter = service._filter

        service.searchUsersById(self.DEFAULT_ID, self.DEFAULT_KEYVALUE)

        mockFilter.createFilter.assert_called_with(dict(
            field='userId',
            operator='eq',
            value=[ self.DEFAULT_ID ]
        ))

    def test_searchUserByIdPassesKeyValuesToPaging(self, service):
        mockPaging = service._paging

        service.searchUsersById(self.DEFAULT_ID, self.DEFAULT_KEYVALUE)

        mockPaging.assert_called_with(self.DEFAULT_KEYVALUE)

    def test_searchUserByIdPassesCreatedFilterAndPagingToQuery(self, service):
        mockDB = service._repo
        
        service.searchUsersById(self.DEFAULT_ID, self.DEFAULT_KEYVALUE)

        mockDB.searchUser.assert_called_with(
            [ self.MOCKFILTER_DEFAULT_RETURN ],
            self.MOCKPAGING_DEFAULT_RETURN,
        )

    def test_searchUserByIdReturnsWhatDBReturns(self, service):
        mockDB = service._repo
        
        response = service.searchUsersById(self.DEFAULT_ID, self.DEFAULT_KEYVALUE)

        assert response == self.MOCKDB_DEFAULT_RETURN

class TestSearchPostsByKeyValues:
    MOCKDB_DEFAULT_RETURN = dict(
        posts=[ dict(userId='11111111') ],
        returnCount=1,
        matchedCount=1,
    )
    MOCKDB_USER_DEFAULT_RETURN = dict(
        users=[ dict(userId='11111111', name='Alan')],
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
            [ self.MOCKFILTER_DEFAULT_RETURN ],
            self.MOCKPAGING_DEFAULT_RETURN
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
            [ self.MOCKFILTER_DEFAULT_RETURN ]
        )

    def test_searchPostByKeyValuesReturnWhatReturnedFromBothQueries(self, service):
        expectedResult = self.MOCKDB_DEFAULT_RETURN.copy()
        expectedResult['posts'][0]['user'] = self.MOCKDB_USER_DEFAULT_RETURN['users'][0]

        searchResult = service.searchPostsByKeyValues(self.DEFAULT_KEYVALUE)

        assert searchResult == expectedResult


    # what should I do when no user was found?