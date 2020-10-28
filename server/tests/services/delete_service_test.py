# -*- coding: utf-8 -*-
"""
This file houses tests for delete_sevice.py
"""
import pytest

import tests.mocks as mocks
import server.exceptions as exceptions
from tests.helpers import create_mock_entities, create_mock_entity_fromattrs
from server.database.filter import PrimitiveFilter
from server.services.delete_service import DeleteService

TEST_DEFAULT_USERID = '11223344'
TEST_DEFAULT_POSTID = '22334455'
TEST_DEFAULT_THREADID = '22123123'


@pytest.fixture(scope='function')
def delete_service():
    session_user = create_mock_entity_fromattrs(dict(userId=TEST_DEFAULT_USERID))

    mock_repo = mocks.createMockRepo()
    mock_session = mocks.createMockSessionService()
    mock_session.get_user.return_value = session_user
    service = DeleteService(mock_repo, mock_session)
    return service


class TestUserDeleteService:
    def test_deleteUserByIdShouldPassUserIdToRepoAsFilter(self, delete_service):
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='userId', value=[ TEST_DEFAULT_USERID ],
        ))

        delete_service.deleteUserById(TEST_DEFAULT_USERID)

        mock_repo.deleteUser.assert_called_once()
        argPassed, *_ = mock_repo.deleteUser.call_args[0]
        assert argPassed == expectedFilter

    def test_deleteUserByIdShouldRaiseExceptionWhenNoId(self, delete_service):
        no_id_patterns = [None, '', ]

        for userid in no_id_patterns:
            with pytest.raises(exceptions.IdNotSpecifiedError):
                delete_service.deleteUserById(userid)

    def test_deleteUserByIdShouldRaiseExceptionWhenAuthorizationFail(self, delete_service):
        invalid_session_users = [
            None,
            create_mock_entity_fromattrs(dict(userId='some_random_id')),
        ]

        for user in invalid_session_users:
            delete_service._session.get_user.return_value = user

            with pytest.raises(exceptions.UnauthorizedError):
                delete_service.deleteUserById(TEST_DEFAULT_USERID)

    def test_deleteUserByIdShouldNotCallRepoWhenAuthorizationFail(self, delete_service):
        invalid_session_users = [
            None,
            create_mock_entity_fromattrs(dict(userId='some_random_id')),
        ]
        mock_repo = delete_service._repo
        
        for user in invalid_session_users:
            delete_service._session.get_user.return_value = user

            try:
                delete_service.deleteUserById(TEST_DEFAULT_USERID)
            except Exception:
                pass

        assert mock_repo.deleteUser.call_count == 0

    def test_deleteUserByIdShouldReturnDeleteResult(self, delete_service):
        mock_repo = delete_service._repo
        service_return = dict( deleteCount=1 )
        mock_repo.deleteUser.return_value = service_return

        rv = delete_service.deleteUserById(TEST_DEFAULT_USERID)

        assert rv == service_return


class TestPostDeleteService:
    POST_ATTRSET = [
        dict(userId=TEST_DEFAULT_USERID, postId=TEST_DEFAULT_POSTID),
    ]

    @pytest.fixture(scope='function', autouse=True)
    def applyMocks(self, delete_service):
        mock_posts = create_mock_entities(self.POST_ATTRSET)
        delete_service._repo.searchPost.return_value = {
            'posts': mock_posts,
            'returnCount': len(mock_posts),
            'matchedCountCount': len(mock_posts),
        }

    def test_deletePostByIdShouldPassPostIdToServiceAsFilter(self, delete_service):
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='postId', value=[ TEST_DEFAULT_POSTID ]
        ))

        delete_service.deletePostById(TEST_DEFAULT_POSTID)

        assert mock_repo.deletePost.call_count == 1
        filterPassed, *_ = mock_repo.deletePost.call_args[0]
        assert filterPassed == expectedFilter

    def test_deletePostByIdShouldRaiseExceptionWhenNoId(self, delete_service):
        noid_patterns = [None, '', ]

        for postid in noid_patterns:
            with pytest.raises(exceptions.IdNotSpecifiedError):
                delete_service.deletePostById(postid)

    def test_deletePostByIdShouldLookupPostOnRepo(self, delete_service):
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='postId', value=[ TEST_DEFAULT_POSTID ]
        ))

        delete_service.deletePostById(TEST_DEFAULT_POSTID)

        assert mock_repo.searchPost.call_count == 1
        filterPassed, *_ = mock_repo.searchPost.call_args[0]
        assert filterPassed == expectedFilter

    def test_deletePostByIdShouldRaiseExceptionWhenUserIdFromRepoNotMatchSession(self, delete_service):
        post_attributes = [ dict(postId=TEST_DEFAULT_POSTID, userId='random_id') ]
        mock_repo = delete_service._repo
        mock_repo.searchPost.return_value = dict(
            posts=create_mock_entities(post_attributes),
            matchedCount=1,
            returnCount=1,
        )

        with pytest.raises(exceptions.UnauthorizedError):
            delete_service.deletePostById(TEST_DEFAULT_POSTID)

    def test_deletePostByIdShouldNotCallDeleteWhenAuthorizeFail(self, delete_service):
        post_attributes = [ dict(postId=TEST_DEFAULT_POSTID, userId='random_id') ]
        mock_repo = delete_service._repo
        mock_repo.searchPost.return_value = dict(
            posts=create_mock_entities(post_attributes),
            matchedCount=1,
            returnCount=1,
        )

        try:
            delete_service.deletePostById(TEST_DEFAULT_POSTID)
        except Exception:
            pass

        assert mock_repo.deletePost.call_count == 0
    
    def test_deleteByIdShouldReturnDeleteResult(self, delete_service):
        mock_repo = delete_service._repo
        service_return = dict( deleteCount=1 )
        mock_repo.deletePost.return_value = service_return

        rv = delete_service.deletePostById(TEST_DEFAULT_POSTID)

        assert rv == service_return


class TestThreadDeleteService:
    THREAD_ATTRSET = [
        dict(userId=TEST_DEFAULT_USERID, threadId=TEST_DEFAULT_THREADID),
    ]

    @pytest.fixture(scope='function', autouse=True)
    def applyMocks(self, delete_service):
        mock_threads = create_mock_entities(self.THREAD_ATTRSET)
        delete_service._repo.searchThread.return_value = {
            'threads': mock_threads,
            'returnCount': len(mock_threads),
            'matchedCountCount': len(mock_threads),
        }

    def test_deleteThreadByIdShouldPassThreadIdToServiceAsFilter(self, delete_service):
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='threadId', value=[ TEST_DEFAULT_THREADID ]
        ))

        delete_service.deleteThreadById(TEST_DEFAULT_THREADID)

        assert mock_repo.deleteThread.call_count == 1
        filterPassed, *_ = mock_repo.deleteThread.call_args[0]
        assert filterPassed == expectedFilter

    def test_deleteThreadByIdShouldRaiseExceptionWhenNoId(self, delete_service):
        noid_patterns = [None, '']

        for threadid in noid_patterns:
            with pytest.raises(exceptions.IdNotSpecifiedError):
                delete_service.deleteThreadById(threadid)

    def test_deleteThreadByIdShouldLookupThreadOnRepo(self, delete_service):
        mock_repo = delete_service._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='threadId', value=[ TEST_DEFAULT_THREADID ]
        ))

        delete_service.deleteThreadById(TEST_DEFAULT_THREADID)

        assert mock_repo.searchThread.call_count == 1
        filterPassed, *_ = mock_repo.searchThread.call_args[0]
        assert filterPassed == expectedFilter

    def test_deleteThreadByIdShouldRaiseExceptionWhenUserIdFromRepoNotMatchSession(self, delete_service):
        thread_attributes = [ dict(threadId=TEST_DEFAULT_THREADID, userId='random_id') ]
        mock_repo = delete_service._repo
        mock_repo.searchThread.return_value = dict(
            threads=create_mock_entities(thread_attributes),
            matchedCount=1,
            returnCount=1,
        )

        with pytest.raises(exceptions.UnauthorizedError):
            delete_service.deleteThreadById(TEST_DEFAULT_THREADID)

    def test_deleteThreadByIdShouldNotCallDeleteWhenAuthorizeFail(self, delete_service):
        thread_attributes = [ dict(threadId=TEST_DEFAULT_THREADID, userId='random_id') ]
        mock_repo = delete_service._repo
        mock_repo.searchThread.return_value = dict(
            threads=create_mock_entities(thread_attributes),
            matchedCount=1,
            returnCount=1,
        )

        try:
            delete_service.deleteThreadById(TEST_DEFAULT_THREADID)
        except Exception:
            pass

        assert mock_repo.deleteThread.call_count == 0
    
    def test_deleteByIdShouldReturnDeleteResult(self, delete_service):
        mock_repo = delete_service._repo
        service_return = dict( deleteCount=1 )
        mock_repo.deleteThread.return_value = service_return

        rv = delete_service.deleteThreadById(TEST_DEFAULT_THREADID)

        assert rv == service_return
