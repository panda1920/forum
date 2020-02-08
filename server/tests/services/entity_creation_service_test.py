# -*- coding: utf-8 -*-
"""
This file houses tests for entity_creation_service.py
"""

import pytest
from unittest.mock import ANY

import tests.mocks as mocks
import server.exceptions as exceptions
from server.services.entity_creation_service import EntityCreationService

@pytest.fixture(scope='function')
def service():
    mockDB = mocks.createMockDB()
    mockFilter = mocks.createMockFilter()
    yield EntityCreationService(mockDB, mockFilter)

class TestSignupUser:
    DEFAULT_KEYVALUES = dict(
        userName='tommy@myforumwebapp.com',
        password='12345678',
    )
    DEFAULT_SEARCHUSER_RETURN = dict(
        users=[],
        returnCount=0,
        matchedCount=0,
    )
    DEFAULT_CREATED_FILTER = 'some_filter'

    @pytest.fixture(scope='function', autouse=True)
    def setupDefaultReturns(self, service):
        service._repo.searchUser.return_value = self.DEFAULT_SEARCHUSER_RETURN
        service._filter.createFilter.return_value = self.DEFAULT_CREATED_FILTER

    def test_signupCalls2CRUDMethods(self, service):
        mockDB = service._repo
        mockFilter = service._filter

        service.signup(self.DEFAULT_KEYVALUES)

        mockFilter.createFilter.assert_called_with(dict(
            field='userName',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['userName'] ],
        ))
        mockDB.searchUser.assert_called_with(self.DEFAULT_CREATED_FILTER)
        mockDB.createUser.assert_called_with(dict(
            **self.DEFAULT_KEYVALUES,
            displayName='tommy'
        ))

    def test_sigupRaisesExceptionWhenSearchUserReturnsUsers(self, service):
        mockDB = service._repo
        mockDB.searchUser.return_value = dict(
            users=['some_user'],
            returnCount=1,
            matchedCount=1,
        )

        with pytest.raises(exceptions.DuplicateUserError):
            service.signup(self.DEFAULT_KEYVALUES)

        assert mockDB.createUser.call_count == 0

    def test_signupPropagatesExceptionFromSearchUser(self, service):
        exception = exceptions.ServerMiscError
        service._repo.searchUser.side_effect = exception()

        with pytest.raises(exception):
            service.signup(self.DEFAULT_KEYVALUES)

    def test_signupPropagatesExceptionFromCreateUser(self, service):
        exception = exceptions.ServerMiscError
        service._repo.createUser.side_effect = exception()

        with pytest.raises(exception):
            service.signup(self.DEFAULT_KEYVALUES)

    def test_signUpRaisesExceptionWhenKeyValueMissingUsername(self, service):
        exception = exceptions.EntityValidationError
        keyValues = dict( offset=30, password='222222')

        with pytest.raises(exception):
            service.signup(keyValues)

class TestCreateNewPost:
    DEFAULT_KEYVALUES = dict(
        content='This is test content',
        random_key1='key1',
        random_key2='key2',
    )

    def test_createNewPostPassesDefaultContentAndUserIdToDB(self, service):
        mockDB = service._repo
        
        service.createNewPost(self.DEFAULT_KEYVALUES)

        mockDB.createPost.call_count == 1
        mockDB.createPost.assert_called_with(dict(
            content=self.DEFAULT_KEYVALUES['content'],
            userId=ANY
        ))

    def test_createNewPostExecutesWithoutExceptionWhenNoContent(self, service):
        keyValues = {}
        mockDB = service._repo

        service.createNewPost(keyValues)

        mockDB.createPost.call_count == 1