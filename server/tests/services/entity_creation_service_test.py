# -*- coding: utf-8 -*-
"""
This file houses tests for entity_creation_service.py
"""

import pytest

import tests.mocks as mocks
import server.exceptions as exceptions
from server.services.entity_creation_service import EntityCreationService
from server.entity import Thread

OWNER_ID = '1'
DEFAULT_SESSION_USER = dict(userId=OWNER_ID)
CREATE_USER_RETURN = dict(createdCount=1, createdId='test_inserted_user')
CREATE_POST_RETURN = dict(createdCount=1, createdId='test_inserted_post')
CREATE_THREAD_RETURN = dict(createdCount=1, createdId='test_inserted_thread')


@pytest.fixture(scope='function')
def service():
    mock_repo = mocks.createMockRepo()
    mock_repo.createUser.return_value = CREATE_USER_RETURN
    mock_repo.createPost.return_value = CREATE_POST_RETURN
    mock_repo.createThread.return_value = CREATE_THREAD_RETURN
    
    mock_filter = mocks.createMockFilter()

    mock_session = mocks.createMockSessionService()
    
    yield EntityCreationService(mock_repo, mock_filter, mock_session)


class TestSignupUser:
    DEFAULT_SEARCHUSER_RETURN = dict(
        users=[],
        returnCount=0,
        matchedCount=0,
    )
    DEFAULT_CREATED_FILTER = 'some_filter'
    DEFAULT_ATTRS = dict(
        userName='tommy@myforumwebapp.com',
        password='12345678',
    )

    @pytest.fixture(scope='function')
    def mock_user(self):
        mock_user = mocks.createMockEntity()
        for attr, value in self.DEFAULT_ATTRS.items():
            setattr(mock_user, attr, value)
        # mock_user.to_create.return_value = self.DEFAULT_ATTRS

        yield mock_user

    @pytest.fixture(scope='function', autouse=True)
    def setupDefaultReturns(self, service):
        service._repo.searchUser.return_value = self.DEFAULT_SEARCHUSER_RETURN
        service._filter.createFilter.return_value = self.DEFAULT_CREATED_FILTER

    def test_signupCalls2CRUDMethods(self, service, mock_user):
        mock_repo = service._repo
        mock_filter = service._filter

        service.signup(mock_user)

        mock_filter.createFilter.assert_called_with(dict(
            field='userName',
            operator='eq',
            value=[ mock_user.userName ],
        ))
        mock_repo.searchUser.assert_called_with(self.DEFAULT_CREATED_FILTER)
        mock_repo.createUser.assert_called_with(mock_user)

    def test_signupCreatesDefaultDisplayNameaAndImageUrl(self, service, mock_user):
        service.signup(mock_user)

        # check that service sets default values
        assert mock_user.displayName == 'tommy'
        assert mock_user.imageUrl == EntityCreationService.GENERIC_PORTRAIT_IMAGE_URL

    def test_sigupRaisesExceptionWhenSearchUserReturnsUsers(self, service, mock_user):
        mock_repo = service._repo
        mock_repo.searchUser.return_value = dict(
            users=['some_user'],
            returnCount=1,
            matchedCount=1,
        )

        with pytest.raises(exceptions.DuplicateUserError):
            service.signup(mock_user)

        assert mock_repo.createUser.call_count == 0

    def test_sigupRaisesExceptionWhenUserLacksUsername(self, service):
        mock_user = mocks.createMockEntity()

        with pytest.raises(exceptions.EntityValidationError):
            service.signup(mock_user)

    def test_signupPropagatesExceptionFromSearchUser(self, service, mock_user):
        exception = exceptions.ServerMiscError
        service._repo.searchUser.side_effect = exception()

        with pytest.raises(exception):
            service.signup(mock_user)

    def test_signupPropagatesExceptionFromCreateUser(self, service, mock_user):
        exception = exceptions.ServerMiscError
        service._repo.createUser.side_effect = exception()

        with pytest.raises(exception):
            service.signup(mock_user)

    def test_signupShouldReturnResultFromRepo(self, service, mock_user):
        result = service.signup(mock_user)
        
        assert result == CREATE_USER_RETURN


class TestCreateNewPost:
    DEFAULT_ATTRS = dict(
        threadId='owner_thread_id',
        content='This is test content',
        random_key1='key1',
        random_key2='key2',
    )

    @pytest.fixture(scope='function')
    def mock_post(self):
        mock_post = mocks.createMockEntity()
        for attr, value in self.DEFAULT_ATTRS.items():
            setattr(mock_post, attr, value)

        yield mock_post

    @pytest.fixture(scope='function', autouse=True)
    def setup_defaultreturn(self, service):
        service._session.get_user.return_value = DEFAULT_SESSION_USER

    def test_createNewPostShouldPassDefaultKeyValuesToRepo(self, service, mock_post):
        mock_repo = service._repo
        
        service.createNewPost(mock_post)

        mock_repo.createPost.call_count == 1
        mock_repo.createPost.assert_called_with(mock_post)

    def test_createNewPostShouldInsertSessionUserIdAsItsOwner(self, service, mock_post):
        repo = service._repo
        expected_ownerid = DEFAULT_SESSION_USER['userId']

        service.createNewPost(mock_post)

        post_passed, *_ = repo.createPost.call_args_list[0][0]
        assert getattr(post_passed, 'userId') == expected_ownerid

    def test_createNewPostShouldReturnResultFromRepo(self, service, mock_post):
        result = service.createNewPost(mock_post)
        
        assert result == CREATE_POST_RETURN

    def test_createNewPostShouldUpdateOwnerThread(self, service, mock_post):
        mock_repo = service._repo
        mock_filter = service._filter
        expectedFilter = 'test_filter_threadId'
        mock_filter.createFilter.return_value = expectedFilter

        service.createNewPost(mock_post)

        filter, _ = mock_repo.updateThread.call_args_list[0][0]
        mock_filter.createFilter.assert_any_call(dict(
            field='threadId', operator='eq', value=[ self.DEFAULT_ATTRS['threadId'] ]
        ))
        assert filter == expectedFilter

    def test_createNewPostShouldUpdatePostCountAndLastPostOnOwnerThread(self, service, mock_post):
        mock_repo = service._repo

        result = service.createNewPost(mock_post)

        _, update_thread = mock_repo.updateThread.call_args_list[0][0]
        assert isinstance(update_thread, Thread)
        assert getattr(update_thread, 'increment') == 'postCount'
        assert getattr(update_thread, 'lastPostId') == result['createdId']


class TestCreateNewThread:
    DEFAULT_ATTRS = dict(
        title='test_title',
        subject='test_subject',
    )

    @pytest.fixture(scope='function')
    def mock_thread(self):
        mock_thread = mocks.createMockEntity()
        for attr, value in self.DEFAULT_ATTRS.items():
            setattr(mock_thread, attr, value)

        yield mock_thread

    @pytest.fixture(scope='function', autouse=True)
    def setup_defaultreturn(self, service):
        service._session.get_user.return_value = DEFAULT_SESSION_USER

    def test_createNewThreadShouldPassDefaultKeyValuesToDB(self, service, mock_thread):
        mock_repo = service._repo
        
        service.createNewThread(mock_thread)

        mock_repo.createThread.call_count == 1
        mock_repo.createThread.assert_called_with(mock_thread)

    def test_createNewThreadGeneratesDefaultValues(self, service, mock_thread):
        mock_repo = service._repo

        service.createNewThread(mock_thread)

        thread_passed, *_ = mock_repo.createThread.call_args_list[0][0]
        assert thread_passed.lastPostId is None
        assert thread_passed.views == 0
        assert thread_passed.postCount == 0

    def test_createNewThreadShouldInsertSessionUserIdAsItsOwner(self, service, mock_thread):
        repo = service._repo
        expected_ownerid = DEFAULT_SESSION_USER['userId']

        service.createNewThread(mock_thread)

        thread_passed, *_ = repo.createThread.call_args_list[0][0]
        assert getattr(thread_passed, 'userId') == expected_ownerid

    def test_createNewThreadShouldReturnResultFromRepo(self, service, mock_thread):
        result = service.createNewThread(mock_thread)
        
        assert result == CREATE_THREAD_RETURN
