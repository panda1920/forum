# -*- coding: utf-8 -*-
"""
This file houses tests for delete_sevice.py
"""
import pytest

import tests.mocks as mocks
import server.exceptions as exceptions
from server.database.filter import PrimitiveFilter
from server.services.delete_service import DeleteService

TEST_DEFAULT_USERID = '11223344'
TEST_DEFAULT_POSTID = '22334455'
TEST_DEFAULT_THREADID = '22123123'


@pytest.fixture(scope='function')
def delete_service():
    mock_repo = mocks.createMockDB()
    mock_session = mocks.createMockSessionService()
    mock_session.get_user.return_value = dict(userId=TEST_DEFAULT_USERID)
    service = DeleteService(mock_repo, mock_session)
    return service


class TestUserDeleteService:
    def test_deleteUserByKeyValuesShouldPassUserIdToRepoAsFilter(self, delete_service):
        keyValues = dict(userId=TEST_DEFAULT_USERID)
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='userId', value=[ TEST_DEFAULT_USERID ],
        ))

        delete_service.deleteUserByKeyValues(keyValues)

        mock_repo.deleteUser.assert_called_once()
        argPassed, *_ = mock_repo.deleteUser.call_args[0]
        assert argPassed == expectedFilter

    def test_deleteUserByKeyValuesShouldRaiseExceptionWhenNoId(self, delete_service):
        keyValues = {}

        with pytest.raises(exceptions.IdNotSpecifiedError):
            delete_service.deleteUserByKeyValues(keyValues)

    def test_deleteUserByKeyValuesShouldRaiseExceptionWhenAuthorizationFail(self, delete_service):
        keyValues = dict(userId=TEST_DEFAULT_USERID)
        invalid_session_users = [
            None, dict(userId='some_random_id')
        ]

        for user in invalid_session_users:
            delete_service._session.get_user.return_value = user

            with pytest.raises(exceptions.UnauthorizedError):
                delete_service.deleteUserByKeyValues(keyValues)

    def test_deleteUserByKeyValuesShouldNotCallRepoWhenAuthorizationFail(self, delete_service):
        keyValues = dict(userId=TEST_DEFAULT_USERID)
        delete_service._session.get_user.return_value = None
        mock_repo = delete_service._repo

        try:
            delete_service.deleteUserByKeyValues(keyValues)
        except Exception:
            pass

        assert mock_repo.deleteUser.call_count == 0

    def test_deleteUserByKeyValuesShouldReturnDeleteResult(self, delete_service):
        keyValues = dict(userId=TEST_DEFAULT_USERID)
        mock_repo = delete_service._repo
        service_return = dict( deleteCount=1 )
        mock_repo.deleteUser.return_value = service_return

        rv = delete_service.deleteUserByKeyValues(keyValues)

        assert rv == service_return


class TestPostDeleteService:
    SEARCHPOST_DEFAULT_RETURN = dict(
        posts=[ dict(userId=TEST_DEFAULT_USERID, postId=TEST_DEFAULT_POSTID) ],
        matchedCount=1,
        returnCount=1,
    )

    @pytest.fixture(scope='function', autouse=True)
    def applyMocks(self, delete_service):
        delete_service._repo.searchPost.return_value = self.SEARCHPOST_DEFAULT_RETURN

    def test_deletePostByKeyValuesShouldPassPostIdToServiceAsFilter(self, delete_service):
        keyValues = dict(postId=TEST_DEFAULT_POSTID)
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='postId', value=[ TEST_DEFAULT_POSTID ]
        ))

        delete_service.deletePostByKeyValues(keyValues)

        assert mock_repo.deletePost.call_count == 1
        filterPassed, *_ = mock_repo.deletePost.call_args[0]
        assert filterPassed == expectedFilter

    def test_deletePostByKeyValuesShouldRaiseExceptionWhenNoId(self, delete_service):
        keyValues = {}

        with pytest.raises(exceptions.IdNotSpecifiedError):
            delete_service.deletePostByKeyValues(keyValues)

    def test_deletePostByKeyValuesShouldLookupPostOnRepo(self, delete_service):
        keyValues = dict(postId=TEST_DEFAULT_POSTID)
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='postId', value=[ TEST_DEFAULT_POSTID ]
        ))

        delete_service.deletePostByKeyValues(keyValues)

        assert mock_repo.searchPost.call_count == 1
        filterPassed, *_ = mock_repo.searchPost.call_args[0]
        assert filterPassed == expectedFilter

    def test_deletePostByKeyValuesShouldRaiseExceptionWhenUserIdFromRepoNotMatchSession(self, delete_service):
        keyValues = dict(postId=TEST_DEFAULT_POSTID)
        mock_repo = delete_service._repo
        mock_repo.searchPost.return_value = dict(
            posts=[ dict(postId=TEST_DEFAULT_POSTID, userId='some_random_id') ],
            matchedCount=1,
            returnCount=1,
        )

        with pytest.raises(exceptions.UnauthorizedError):
            delete_service.deletePostByKeyValues(keyValues)

    def test_deletePostByKeyValuesShouldNotCallDeleteWhenAuthorizeFail(self, delete_service):
        keyValues = dict(postId=TEST_DEFAULT_POSTID)
        mock_repo = delete_service._repo
        mock_repo.searchPost.return_value = dict(
            posts=[ dict(postId=TEST_DEFAULT_POSTID, userId='some_random_id') ],
            matchedCount=1,
            returnCount=1,
        )

        try:
            delete_service.deletePostByKeyValues(keyValues)
        except Exception:
            pass

        assert mock_repo.deletePost.call_count == 0
    
    def test_deleteByKeyValuesShouldReturnDeleteResult(self, delete_service):
        keyValues = dict(postId=TEST_DEFAULT_POSTID)
        mock_repo = delete_service._repo
        service_return = dict( deleteCount=1 )
        mock_repo.deletePost.return_value = service_return

        rv = delete_service.deletePostByKeyValues(keyValues)

        assert rv == service_return


class TestThreadDeleteService:
    SEARCHTHREAD_DEFAULT_RETURN = dict(
        threads=[ dict(userId=TEST_DEFAULT_USERID, postId=TEST_DEFAULT_POSTID) ],
        matchedCount=1,
        returnCount=1,
    )

    @pytest.fixture(scope='function', autouse=True)
    def applyMocks(self, delete_service):
        delete_service._repo.searchThread.return_value = self.SEARCHTHREAD_DEFAULT_RETURN

    def test_deleteThreadByKeyValuesShouldPassThreadIdToServiceAsFilter(self, delete_service):
        keyValues = dict(threadId=TEST_DEFAULT_THREADID)
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='threadId', value=[ TEST_DEFAULT_THREADID ]
        ))

        delete_service.deleteThreadByKeyValues(keyValues)

        assert mock_repo.deleteThread.call_count == 1
        filterPassed, *_ = mock_repo.deleteThread.call_args[0]
        assert filterPassed == expectedFilter

    def test_deleteThreadByKeyValuesShouldRaiseExceptionWhenNoId(self, delete_service):
        keyValues = {}

        with pytest.raises(exceptions.IdNotSpecifiedError):
            delete_service.deleteThreadByKeyValues(keyValues)

    def test_deleteThreadByKeyValuesShouldLookupThreadOnRepo(self, delete_service):
        keyValues = dict(threadId=TEST_DEFAULT_THREADID)
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='threadId', value=[ TEST_DEFAULT_THREADID ]
        ))

        delete_service.deleteThreadByKeyValues(keyValues)

        assert mock_repo.searchThread.call_count == 1
        filterPassed, *_ = mock_repo.searchThread.call_args[0]
        assert filterPassed == expectedFilter

    def test_deleteThreadByKeyValuesShouldRaiseExceptionWhenUserIdFromRepoNotMatchSession(self, delete_service):
        keyValues = dict(threadId=TEST_DEFAULT_THREADID)
        mock_repo = delete_service._repo
        mock_repo.searchThread.return_value = dict(
            threads=[ dict(threadId=TEST_DEFAULT_THREADID, userId='some_random_id') ],
            matchedCount=1,
            returnCount=1,
        )

        with pytest.raises(exceptions.UnauthorizedError):
            delete_service.deleteThreadByKeyValues(keyValues)

    def test_deleteThreadByKeyValuesShouldNotCallDeleteWhenAuthorizeFail(self, delete_service):
        keyValues = dict(threadId=TEST_DEFAULT_THREADID)
        mock_repo = delete_service._repo
        mock_repo.searchThread.return_value = dict(
            threads=[ dict(threadId=TEST_DEFAULT_THREADID, userId='some_random_id') ],
            matchedCount=1,
            returnCount=1,
        )

        try:
            delete_service.deleteThreadByKeyValues(keyValues)
        except Exception:
            pass

        assert mock_repo.deleteThread.call_count == 0
    
    def test_deleteByKeyValuesShouldReturnDeleteResult(self, delete_service):
        keyValues = dict(threadId=TEST_DEFAULT_THREADID)
        mock_repo = delete_service._repo
        service_return = dict( deleteCount=1 )
        mock_repo.deleteThread.return_value = service_return

        rv = delete_service.deleteThreadByKeyValues(keyValues)

        assert rv == service_return
