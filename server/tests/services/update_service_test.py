# -*- coding: utf-8 -*-
"""
This file houses test for update_service.py
"""
from unittest.mock import ANY


import pytest

from tests import mocks
import server.exceptions as exceptions
from server.database.filter import PrimitiveFilter
from server.services.update_service import UpdateService

TEST_SESSION_USER = dict(userId='test_user_id')


@pytest.fixture(scope='function')
def setup_service():
    mock_repo = mocks.createMockDB()
    mock_session = mocks.createMockSessionService()
    mock_session.get_user.return_value = TEST_SESSION_USER
    
    return UpdateService(mock_repo, PrimitiveFilter, mock_session)


class TestUserUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    DEFAULT_SEARCH_RETURN = dict(
        users=[ dict(userId=TEST_SESSION_USER['userId']) ],
        returnCount=1,
        matchedCount=1,
    )
    DEFAULT_KEYVALUES = dict(
        userId='0',
        displayName='Bobby'
    )
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_repo = setup_service._repo
        mock_repo.searchUser.return_value = self.DEFAULT_SEARCH_RETURN
        mock_repo.updateUser.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updateUserByKeyValuesShouldCallSearchForUserInformation(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_KEYVALUES['userId'] ]
        ))

        setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.searchUser.assert_called_with(expectedFilter)

    def test_updateUserByKeyValuesShouldRaiseExceptionWhenReturnedOwnerNotMatchSession(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

    def test_updateUserByKeyValuesShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)
        except Exception:
            pass

        assert setup_service._repo.updateUser.call_count == 0

    def test_updateUserByKeyValuesShouldPassCreatedFilterToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_KEYVALUES['userId'] ]
        ))

        setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updateUser.assert_called_with(expectedFilter, ANY)

    def test_updateUserByKeyValuesShouldRaiseExceptionWhenNoUserId(self, setup_service):
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues.pop('userId')

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateUserByKeyValues(keyValues)

    def test_updateUserShouldPassAllKeyValuesExceptIdAsUpdateValue(self, setup_service):
        mock_repo = setup_service._repo
        expectedUpdate = self.DEFAULT_KEYVALUES.copy()
        expectedUpdate.pop('userId')

        setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updateUser.assert_called_with(ANY, expectedUpdate)

    def test_updateUserByKeyValuesShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

        assert result == self.DEFAULT_REPOUPDATE_RESULT


class TestPostUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    DEFAULT_SEARCH_RETURN = dict(
        posts=[ dict(postId=0, userId=TEST_SESSION_USER['userId']) ],
        returnCount=1,
        matchedCount=1,
    )
    DEFAULT_KEYVALUES = dict(
        postId='0',
        content='Hello this is my first post'
    )
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_repo = setup_service._repo
        mock_repo.searchPost.return_value = self.DEFAULT_SEARCH_RETURN
        mock_repo.updatePost.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updatePostByKeyValuesShouldCallSearchForPostInformation(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_KEYVALUES['postId'] ]
        ))

        setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.searchPost.assert_called_with(expectedFilter)

    def test_updatePostByKeyValuesShouldRaiseExceptionWhenReturnedOwnerNotMatchSession(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

    def test_updatePostByKeyValuesShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)
        except Exception:
            pass

        assert setup_service._repo.updatePost.call_count == 0

    def test_updatePostByKeyValuesShouldPassCreatedFilterToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_KEYVALUES['postId'] ]
        ))

        setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updatePost.assert_called_with(expectedFilter, ANY)

    def test_updatePostByKeyValuesShouldRaiseExceptionWhenNoPostId(self, setup_service):
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues.pop('postId')

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updatePostByKeyValues(keyValues)

    def test_updatePostShouldPassAllKeyValuesExceptIdAsUpdateValue(self, setup_service):
        mock_repo = setup_service._repo
        expectedUpdate = self.DEFAULT_KEYVALUES.copy()
        expectedUpdate.pop('postId')

        setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updatePost.assert_called_with(ANY, expectedUpdate)

    def test_updatePostByKeyValuesShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

        assert result == self.DEFAULT_REPOUPDATE_RESULT


class TestThreadUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    DEFAULT_SEARCH_RETURN = dict(
        threads=[ dict(threadId=0, userId=TEST_SESSION_USER['userId']) ],
        returnCount=1,
        matchedCount=1,
    )
    DEFAULT_KEYVALUES = dict(
        threadId='0',
        title='Hello this is my first thread'
    )

    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_repo = setup_service._repo
        mock_repo.searchThread.return_value = self.DEFAULT_SEARCH_RETURN
        mock_repo.updateThread.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updateThreadByKeyValuesShouldCallSearchForThreadInformation(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_KEYVALUES['threadId'] ]
        ))

        setup_service.updateThreadByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.searchThread.assert_called_with(expectedFilter)

    def test_updateThreadByKeyValuesShouldRaiseExceptionWhenReturnedOwnerNotMatchSession(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateThreadByKeyValues(self.DEFAULT_KEYVALUES)

    def test_updateThreadByKeyValuesShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateThreadByKeyValues(self.DEFAULT_KEYVALUES)
        except Exception:
            pass

        assert setup_service._repo.updateThread.call_count == 0

    def test_updateThreadByKeyValuesShouldPassCreatedFilterToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_KEYVALUES['threadId'] ]
        ))

        setup_service.updateThreadByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updateThread.assert_called_with(expectedFilter, ANY)

    def test_updateThreadByKeyValuesShouldRaiseExceptionWhenNoThreadId(self, setup_service):
        keyValues = self.DEFAULT_KEYVALUES.copy()
        keyValues.pop('threadId')

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateThreadByKeyValues(keyValues)

    def test_updateThreadShouldPassAllKeyValuesExceptIdAsUpdateValue(self, setup_service):
        mock_repo = setup_service._repo
        expectedUpdate = self.DEFAULT_KEYVALUES.copy()
        expectedUpdate.pop('threadId')

        setup_service.updateThreadByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updateThread.assert_called_with(ANY, expectedUpdate)

    def test_updateThreadByKeyValuesShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateThreadByKeyValues(self.DEFAULT_KEYVALUES)

        assert result == self.DEFAULT_REPOUPDATE_RESULT
