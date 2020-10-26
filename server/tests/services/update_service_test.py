# -*- coding: utf-8 -*-
"""
This file houses test for update_service.py
"""
from unittest.mock import ANY

import pytest

from tests import mocks
import server.exceptions as exceptions
from tests.helpers import create_mock_entities
from server.database.filter import PrimitiveFilter
from server.services.update_service import UpdateService

TEST_SESSION_USER = dict(userId='test_user_id')


# helper functions
def create_repo_return(entities, name):
    return {
        name: entities,
        'returnCount': len(entities),
        'matchedCount': len(entities),
    }


@pytest.fixture(scope='function')
def setup_service():
    mock_repo = mocks.createMockRepo()
    mock_session = mocks.createMockSessionService()
    mock_session.get_user.return_value = TEST_SESSION_USER
    
    return UpdateService(mock_repo, PrimitiveFilter, mock_session)


class TestUserUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    REPOUSER_ATTRSET = [
        dict(userId=TEST_SESSION_USER['userId']),
    ]
    DEFAULT_USER_ATTRSET = [
        dict(userId='0', displayName='Bobby'),
    ]
    DEFAULT_USER = create_mock_entities(DEFAULT_USER_ATTRSET)[0]
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_users = create_mock_entities(self.REPOUSER_ATTRSET)
        repouser_return = create_repo_return(mock_users, 'users')

        mock_repo = setup_service._repo
        mock_repo.searchUser.return_value = repouser_return
        mock_repo.updateUser.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updateUserShouldCallSearchForUserInformation(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_USER.userId ]
        ))

        setup_service.updateUser(self.DEFAULT_USER)

        mock_repo.searchUser.assert_called_with(expectedFilter)

    def test_updateUserShouldRaiseExceptionWhenReturnedOwnerNotMatchSession(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateUser(self.DEFAULT_USER)

    def test_updateUserShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateUser(self.DEFAULT_USER)
        except Exception:
            pass

        assert setup_service._repo.updateUser.call_count == 0

    def test_updateUserShouldPassCreatedFilterAndUserToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_USER.userId ]
        ))

        setup_service.updateUser(self.DEFAULT_USER)

        mock_repo.updateUser.assert_called_with(expectedFilter, self.DEFAULT_USER)

    def test_updateUserShouldRaiseExceptionWhenNoUserId(self, setup_service):
        attributes = [{ 'displayName': 'test_name' }]
        nouserid_user = create_mock_entities(attributes)[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateUser(nouserid_user)

    def test_updateUserShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateUser(self.DEFAULT_USER)

        assert result == self.DEFAULT_REPOUPDATE_RESULT


class TestPostUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    REPOPOST_ATTRSET = [
        dict(postId='0', userId=TEST_SESSION_USER['userId'], content='test_post_1')
    ]
    DEFAULT_POST_ATTRSET = [
        dict(postId='0', content='Hello this is my first post')
    ]
    DEFAULT_POST = create_mock_entities(DEFAULT_POST_ATTRSET)[0]
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_posts = create_mock_entities(self.REPOPOST_ATTRSET)
        repopost_return = create_repo_return(mock_posts, 'posts')

        mock_repo = setup_service._repo
        mock_repo.searchPost.return_value = repopost_return
        mock_repo.updatePost.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updatePostShouldCallSearchForPostInformation(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_POST.postId ]
        ))

        setup_service.updatePost(self.DEFAULT_POST)

        mock_repo.searchPost.assert_called_with(expectedFilter)

    def test_updatePostShouldRaiseExceptionWhenReturnedOwnerNotMatchSession(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updatePost(self.DEFAULT_POST)

    def test_updatePostShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updatePost(self.DEFAULT_POST)
        except Exception:
            pass

        assert setup_service._repo.updatePost.call_count == 0

    def test_updatePostShouldPassCreatedFilterAndPostToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_POST.postId ]
        ))

        setup_service.updatePost(self.DEFAULT_POST)

        mock_repo.updatePost.assert_called_with(expectedFilter, self.DEFAULT_POST)

    def test_updatePostShouldRaiseExceptionWhenNoPostId(self, setup_service):
        mock_post = create_mock_entities([dict(content='test_content')])[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updatePost(mock_post)

    def test_updatePostShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updatePost(self.DEFAULT_POST)

        assert result == self.DEFAULT_REPOUPDATE_RESULT


class TestThreadUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    REPOTHREAD_ATTRSET = [
        dict(threadId='0', userId=TEST_SESSION_USER['userId'], title='test_thread_1')
    ]
    DEFAULT_THREAD_ATTRSET = [
        dict(threadId='0', title='Hello this is my first thread')
    ]
    DEFAULT_THREAD = create_mock_entities(DEFAULT_THREAD_ATTRSET)[0]

    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_threads = create_mock_entities(self.REPOTHREAD_ATTRSET)
        repothread_return = create_repo_return(mock_threads, 'threads')

        mock_repo = setup_service._repo
        mock_repo.searchThread.return_value = repothread_return
        mock_repo.updateThread.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updateThreadShouldCallSearchForThreadInformation(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_THREAD.threadId ]
        ))

        setup_service.updateThread(self.DEFAULT_THREAD)

        mock_repo.searchThread.assert_called_with(expectedFilter)

    def test_updateThreadShouldRaiseExceptionWhenReturnedOwnerNotMatchSession(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateThread(self.DEFAULT_THREAD)

    def test_updateThreadShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = dict(userId='some_random_id')
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateThread(self.DEFAULT_THREAD)
        except Exception:
            pass

        assert setup_service._repo.updateThread.call_count == 0

    def test_updateThreadShouldPassCreatedFilterToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_THREAD.threadId ]
        ))

        setup_service.updateThread(self.DEFAULT_THREAD)

        mock_repo.updateThread.assert_called_with(expectedFilter, ANY)

    def test_updateThreadShouldRaiseExceptionWhenNoThreadId(self, setup_service):
        mock_thread = create_mock_entities([dict(title='test_title')])[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateThread(mock_thread)

    def test_updateThreadShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateThread(self.DEFAULT_THREAD)

        assert result == self.DEFAULT_REPOUPDATE_RESULT
