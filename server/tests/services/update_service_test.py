# -*- coding: utf-8 -*-
"""
This file houses test for update_service.py
"""
from unittest.mock import ANY
from pathlib import Path

import pytest

from tests import mocks
import server.exceptions as exceptions
from tests.helpers import create_mock_entities, create_mock_entity_fromattrs
from server.database.filter import PrimitiveFilter
from server.services.update_service import UpdateService

DEFAULT_SESSION_USER = create_mock_entity_fromattrs( dict(userId='test_user_id') )
TESTDATA_DIR = Path(__file__).resolve().parents[1] / 'testdata'
DEFAULT_IMAGE = TESTDATA_DIR / 'sample_image.png'
with DEFAULT_IMAGE.open('rb') as f:
    DEFAULT_IMAGE_DATA = f.read()


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
    mock_session.get_user.return_value = DEFAULT_SESSION_USER

    mock_uploader = mocks.createMockPortraitUploadService()
    
    return UpdateService(mock_repo, PrimitiveFilter, mock_session, mock_uploader)


class TestUserUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    REPOUSER_ATTRSET = [
        dict(userId=DEFAULT_SESSION_USER.userId),
    ]
    DEFAULT_USER_ATTRSET = [
        dict(userId='0', displayName='Bobby', portraitImage=DEFAULT_IMAGE_DATA),
    ]
    DEFAULT_USER = create_mock_entities(DEFAULT_USER_ATTRSET)[0]
    DEFAULT_PORTRAIT_URL = 'http://example.com/test_image.png'
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_users = create_mock_entities(self.REPOUSER_ATTRSET)
        repouser_return = create_repo_return(mock_users, 'users')

        mock_repo = setup_service._repo
        mock_repo.searchUser.return_value = repouser_return
        mock_repo.updateUser.return_value = self.DEFAULT_REPOUPDATE_RESULT

        mock_uploader = setup_service._uploader
        mock_uploader.upload.return_value = dict(publicUrl=self.DEFAULT_PORTRAIT_URL)

    def test_updateUserShouldCallSearchForUserInformation(self, setup_service):
        mock_repo = setup_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_USER.userId ]
        ))

        setup_service.updateUser(self.DEFAULT_USER)

        mock_repo.searchUser.assert_called_with(expected_filter)

    def test_updateUserShouldRaiseExceptionWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateUser(self.DEFAULT_USER)

    def test_updateUserShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateUser(self.DEFAULT_USER)
        except Exception:
            pass

        assert setup_service._repo.updateUser.call_count == 0

    def test_updateUserShouldUploadPortraitImage(self, setup_service):
        mock_uploader = setup_service._uploader

        setup_service.updateUser(self.DEFAULT_USER)

        assert mock_uploader.upload.call_count == 1

    def test_updateUserShouldNotUploadWhenNoFilePresent(self, setup_service):
        attrs = self.DEFAULT_USER_ATTRSET[0].copy()
        attrs.pop('portraitImage', None)
        update_user = create_mock_entity_fromattrs(attrs)
        mock_uploader = setup_service._uploader

        setup_service.updateUser(update_user)

        assert mock_uploader.upload.call_count == 0

    def test_updateUserShouldPassCreatedFilterAndUserToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_USER.userId ]
        ))

        setup_service.updateUser(self.DEFAULT_USER)

        filter, user, *_ = mock_repo.updateUser.call_args_list[0][0]
        assert filter == expected_filter
        assert user == self.DEFAULT_USER

    def test_updateUserShouldPassPublicUrlToUpdate(self, setup_service):
        mock_repo = setup_service._repo

        setup_service.updateUser(self.DEFAULT_USER)

        _, user, *_ = mock_repo.updateUser.call_args_list[0][0]
        assert user.imageUrl == self.DEFAULT_PORTRAIT_URL

    def test_updateUserShouldRaiseExceptionWhenNoUserId(self, setup_service):
        attributes = [{ 'displayName': 'test_name' }]
        nouserid_user = create_mock_entities(attributes)[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateUser(nouserid_user)

    def test_updateUserShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateUser(self.DEFAULT_USER)

        assert result == self.DEFAULT_REPOUPDATE_RESULT

    def test_updateUserShouldUpdateSessionUserInfoWithNewUser(self, setup_service):
        mock_session = setup_service._session
        old_users = create_mock_entities(self.REPOUSER_ATTRSET)
        new_users = create_mock_entities( [dict(userId='new_id')] )
        mock_repo = setup_service._repo
        mock_repo.searchUser.side_effect = [
            create_repo_return(old_users, 'users'),
            create_repo_return(new_users, 'users'),
        ]

        setup_service.updateUser(self.DEFAULT_USER)

        assert mock_session.set_user.call_count == 1
        user, *_ = mock_session.set_user.call_args_list[0][0]
        assert user == new_users[0]


class TestPostUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    REPOPOST_ATTRSET = [
        dict(postId='0', userId=DEFAULT_SESSION_USER.userId, content='test_post_1')
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
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_POST.postId ]
        ))

        setup_service.updatePost(self.DEFAULT_POST)

        mock_repo.searchPost.assert_called_with(expected_filter)

    def test_updatePostShouldRaiseExceptionWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updatePost(self.DEFAULT_POST)

    def test_updatePostShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updatePost(self.DEFAULT_POST)
        except Exception:
            pass

        assert setup_service._repo.updatePost.call_count == 0

    def test_updatePostShouldPassCreatedFilterAndPostToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_POST.postId ]
        ))

        setup_service.updatePost(self.DEFAULT_POST)

        mock_repo.updatePost.assert_called_with(expected_filter, self.DEFAULT_POST)

    def test_updatePostShouldRaiseExceptionWhenNoPostId(self, setup_service):
        mock_post = create_mock_entities([dict(content='test_content')])[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updatePost(mock_post)

    def test_updatePostShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updatePost(self.DEFAULT_POST)

        assert result == self.DEFAULT_REPOUPDATE_RESULT


class TestThreadUpdateService:
    DEFAULT_REPOUPDATE_RESULT = dict(updatedCount=1, matchedCount=1)
    REPOTHREAD_ATTRSET = [
        dict(threadId='0', userId=DEFAULT_SESSION_USER.userId, title='test_thread_1')
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
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_THREAD.threadId ]
        ))

        setup_service.updateThread(self.DEFAULT_THREAD)

        mock_repo.searchThread.assert_called_with(expected_filter)

    def test_updateThreadShouldRaiseExceptionWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateThread(self.DEFAULT_THREAD)

    def test_updateThreadShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateThread(self.DEFAULT_THREAD)
        except Exception:
            pass

        assert setup_service._repo.updateThread.call_count == 0

    def test_updateThreadShouldPassCreatedFilterToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_THREAD.threadId ]
        ))

        setup_service.updateThread(self.DEFAULT_THREAD)

        mock_repo.updateThread.assert_called_with(expected_filter, ANY)

    def test_updateThreadShouldRaiseExceptionWhenNoThreadId(self, setup_service):
        mock_thread = create_mock_entities([dict(title='test_title')])[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateThread(mock_thread)

    def test_updateThreadShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateThread(self.DEFAULT_THREAD)

        assert result == self.DEFAULT_REPOUPDATE_RESULT

    def test_viewThreadShouldIncrementParticularThreadInDB(self, setup_service):
        mock_repo = setup_service._repo
        threadId = self.DEFAULT_THREAD.threadId
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='threadId', operator='eq', value=[ threadId ]
        ))

        setup_service.viewThread(threadId)

        assert mock_repo.updateThread.call_count == 1
        searchFilter, update, *_ = mock_repo.updateThread.call_args_list[0][0]
        assert searchFilter == expected_filter
        assert getattr(update, 'increment') == 'views'

    def test_viewThreadShouldReturnUpdateResult(self, setup_service):
        threadId = self.DEFAULT_THREAD.threadId
        expected_result = { 'updatedCount': self.DEFAULT_REPOUPDATE_RESULT['updatedCount'] }

        result = setup_service.viewThread(threadId)

        assert result == expected_result

    def test_viewThreadShouldReturnUpdateResultWhenUpdateFails(self, setup_service):
        threadId = self.DEFAULT_THREAD.threadId
        mock_repo = setup_service._repo
        mock_repo.updateThread.return_value = dict(updatedCount=0, matchedCount=10)
        expected_result = { 'updatedCount': 0 }

        result = setup_service.viewThread(threadId)

        assert result == expected_result

    def test_viewThreadShouldNotUpdateThreadWhenInvalidId(self, setup_service):
        mock_repo = setup_service._repo
        threadIds = [ None, '', ]
        expected_result = { 'updatedCount': 0 }

        for threadId in threadIds:
            result = setup_service.viewThread(threadId)

            assert mock_repo.updateThread.call_count == 0
            assert result == expected_result


class TestBoardUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    REPOBOARD_ATTRSET = [
        dict(boardId='0', userId=DEFAULT_SESSION_USER.userId, title='test_board_1')
    ]
    DEFAULT_BOARD_ATTRSET = [
        dict(boardId='0', title='Hello this is my first board')
    ]
    DEFAULT_BOARD = create_mock_entities(DEFAULT_BOARD_ATTRSET)[0]

    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_boards = create_mock_entities(self.REPOBOARD_ATTRSET)
        repoboard_return = create_repo_return(mock_boards, 'boards')

        mock_repo = setup_service._repo
        mock_repo.searchBoard.return_value = repoboard_return
        mock_repo.updateBoard.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updateBoardShouldCallSearchForBoardInformation(self, setup_service):
        mock_repo = setup_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='boardId', operator='eq', value=[ self.DEFAULT_BOARD.boardId ]
        ))

        setup_service.updateBoard(self.DEFAULT_BOARD)

        mock_repo.searchBoard.assert_called_with(expected_filter)
    
    def test_updateBoardShouldRaiseExceptionWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        with pytest.raises(exceptions.UnauthorizedError):
            setup_service.updateBoard(self.DEFAULT_BOARD)
    
    def test_updateBoardShouldNotUpdateWhenAuthorizationFail(self, setup_service):
        session_user = create_mock_entity_fromattrs( dict(userId='some_random_id') )
        setup_service._session.get_user.return_value = session_user

        try:
            setup_service.updateBoard(self.DEFAULT_BOARD)
        except Exception:
            pass

        assert setup_service._repo.updateBoard.call_count == 0
    
    def test_updateBoardShouldPassCreatedFilterAndEntityToUpdate(self, setup_service):
        mock_repo = setup_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='boardId', operator='eq', value=[ self.DEFAULT_BOARD.boardId ]
        ))

        setup_service.updateBoard(self.DEFAULT_BOARD)

        mock_repo.updateBoard.assert_called_with(expected_filter, self.DEFAULT_BOARD)
    
    def test_updateBoardShouldRaiseExceptionWhenNoBoardId(self, setup_service):
        mock_board = create_mock_entities([dict(title='test_title')])[0]

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateBoard(mock_board)
    
    def test_updateBoardShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateBoard(self.DEFAULT_BOARD)

        assert result == self.DEFAULT_REPOUPDATE_RESULT
