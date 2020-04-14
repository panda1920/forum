# -*- coding: utf-8 -*-
"""
This file houses tests for entity_creation_service.py
"""

import pytest
from unittest.mock import ANY

import tests.mocks as mocks
import server.exceptions as exceptions
from server.services.entity_creation_service import EntityCreationService

OWNER_ID = '1'
DEFAULT_SESSION_USER = dict(userId=OWNER_ID)
CREATE_USER_RETURN = dict(createdCount=1, createdId='test_inserted_user')
CREATE_POST_RETURN = dict(createdCount=1, createdId='test_inserted_post')
CREATE_THREAD_RETURN = dict(createdCount=1, createdId='test_inserted_thread')


@pytest.fixture(scope='function')
def service():
    mock_repo = mocks.createMockDB()
    mock_repo.createUser.return_value = CREATE_USER_RETURN
    mock_repo.createPost.return_value = CREATE_POST_RETURN
    mock_repo.createThread.return_value = CREATE_THREAD_RETURN
    
    mock_filter = mocks.createMockFilter()

    mock_session = mocks.createMockSessionService()
    
    yield EntityCreationService(mock_repo, mock_filter, mock_session)


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
        mock_repo = service._repo
        mock_filter = service._filter

        service.signup(self.DEFAULT_KEYVALUES)

        mock_filter.createFilter.assert_called_with(dict(
            field='userName',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['userName'] ],
        ))
        mock_repo.searchUser.assert_called_with(self.DEFAULT_CREATED_FILTER)
        mock_repo.createUser.assert_called_with(dict(
            **self.DEFAULT_KEYVALUES,
            displayName='tommy',
            imageUrl=EntityCreationService.GENERIC_PORTRAIT_IMAGE_URL
        ))

    def test_sigupRaisesExceptionWhenSearchUserReturnsUsers(self, service):
        mock_repo = service._repo
        mock_repo.searchUser.return_value = dict(
            users=['some_user'],
            returnCount=1,
            matchedCount=1,
        )

        with pytest.raises(exceptions.DuplicateUserError):
            service.signup(self.DEFAULT_KEYVALUES)

        assert mock_repo.createUser.call_count == 0

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

    def test_signupShouldReturnResultFromRepo(self, service):
        result = service.signup(self.DEFAULT_KEYVALUES)
        
        assert result == CREATE_USER_RETURN


class TestCreateNewPost:
    DEFAULT_KEYVALUES = dict(
        userId=OWNER_ID,
        threadId='owner_thread_id',
        content='This is test content',
        random_key1='key1',
        random_key2='key2',
    )

    @pytest.fixture(scope='function', autouse=True)
    def setup_defaultreturn(self, service):
        service._session.get_user.return_value = DEFAULT_SESSION_USER

    def test_createNewPostShouldPassDefaultKeyValuesToRepo(self, service):
        mock_repo = service._repo
        
        service.createNewPost(self.DEFAULT_KEYVALUES)

        mock_repo.createPost.call_count == 1
        mock_repo.createPost.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_createPostShouldRaiseExceptionoWhenSessionUserNotMatchOwner(self, service):
        session_user = dict(userId='2233444')
        service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            service.createNewPost(self.DEFAULT_KEYVALUES)

    def test_createNewPostShouldReturnResultFromRepo(self, service):
        result = service.createNewPost(self.DEFAULT_KEYVALUES)
        
        assert result == CREATE_POST_RETURN

    def test_createNewPostShouldUpdateOwnerThread(self, service):
        mock_repo = service._repo
        mock_filter = service._filter
        expectedFilter = 'test_filter_threadId'
        mock_filter.createFilter.return_value = expectedFilter

        service.createNewPost(self.DEFAULT_KEYVALUES)

        mock_filter.createFilter.assert_any_call(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_KEYVALUES['threadId'] ]
        ))
        mock_repo.updateThread.assert_called_with(expectedFilter, ANY)

    def test_createNewPostShouldUpdatePostCountAndLastPostOnOwnerThread(self, service):
        mock_repo = service._repo

        result = service.createNewPost(self.DEFAULT_KEYVALUES)

        expectedUpdate = dict(increment='posts', lastPostId=result['createdId'])
        mock_repo.updateThread.assert_called_with(ANY, expectedUpdate)


class TestCreateNewThread:
    DEFAULT_KEYVALUES = dict(
        userId=OWNER_ID,
        title='test_title',
        subject='test_subject',
    )

    @pytest.fixture(scope='function', autouse=True)
    def setup_defaultreturn(self, service):
        service._session.get_user.return_value = DEFAULT_SESSION_USER

    def test_createNewThreadShouldPassDefaultKeyValuesToDB(self, service):
        mock_repo = service._repo
        
        service.createNewThread(self.DEFAULT_KEYVALUES)

        mock_repo.createThread.call_count == 1
        mock_repo.createThread.assert_called_with(self.DEFAULT_KEYVALUES)

    def test_createThreadShouldRaiseExceptionoWhenSessionUserNotMatchOwner(self, service):
        session_user = dict(userId='2233444')
        service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            service.createNewThread(self.DEFAULT_KEYVALUES)

    def test_createNewThreadShouldReturnResultFromRepo(self, service):
        result = service.createNewThread(self.DEFAULT_KEYVALUES)
        
        assert result == CREATE_THREAD_RETURN
