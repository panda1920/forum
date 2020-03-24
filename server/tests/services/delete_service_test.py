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


@pytest.fixture(scope='function')
def delete_service():
    mock_repo = mocks.createMockDB()
    mock_context = mocks.createMockFlaskContext()
    mock_context.read_global.return_value = dict(userId=TEST_DEFAULT_USERID)
    service = DeleteService(mock_repo, mock_context)
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

    def test_deleteUserByKeyValuesShouldRaiseExceptionWhenAuthorizationFail(self, delete_service):
        keyValues = dict(userId=TEST_DEFAULT_USERID)
        invalid_session_users = [
            None, dict(userId='some_random_id')
        ]

        for user in invalid_session_users:
            mock_context = delete_service._context
            mock_context.read_global.return_value = user

            with pytest.raises(exceptions.UnauthorizedError):
                delete_service.deleteUserByKeyValues(keyValues)

    def test_deleteUserByKeyValuesShouldNotCallRepoWhenAuthorizationFail(self, delete_service):
        keyValues = dict(userId=TEST_DEFAULT_USERID)
        mock_context = delete_service._context
        mock_context.read_global.return_value = None
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

        assert rv['result'] == service_return


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

    def test_deletePostByKeyValuesShouldRaiseExceptionWhenAuthorizeFail(self, delete_service):
        keyValues = dict(postId=TEST_DEFAULT_POSTID)
        mock_repo = delete_service._repo
        mock_repo.searchPost.return_value = dict(
            posts=[ dict(postId=TEST_DEFAULT_POSTID, userId='some_random_id') ],
            matchedCount=1,
            returnCount=1,
        )

        with pytest.raises(exceptions.UnauthorizedError):
            delete_service.deletePostByKeyValues(keyValues)

    def test_deletePostByKeyValuesShouldNotCallDelete(self, delete_service):
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

        assert rv['result'] == service_return
