# -*- coding: utf-8 -*-
"""
This file houses test for update_service.py
"""

import pytest

from tests import mocks
from server.services.update_service import UpdateService
import server.exceptions as exceptions
from server.database.filter import PrimitiveFilter


@pytest.fixture(scope='function')
def setup_service():
    mock_repo = mocks.createMockDB()
    return UpdateService(mock_repo, PrimitiveFilter)


class TestUserUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    DEFAULT_KEYVALUES = dict(
        userId='0',
        displayName='Bobby'
    )
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_repo = setup_service._repo
        mock_repo.updateUser.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updateUserByKeyValuesShouldPassSearchFilterAndKeyValues(self, setup_service):
        mock_repo = setup_service._repo
        searchFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ self.DEFAULT_KEYVALUES['userId'] ]
        ))
        update = self.DEFAULT_KEYVALUES.copy().pop('userId')

        setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updateUser.assert_called_with(searchFilter, update)

    def test_updateUserByKeyValuesShouldRaiseExceptionWhenNoUserIdWasPassed(self, setup_service):
        keyValues = dict(displayName='Tommy')

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updateUserByKeyValues(keyValues)

    def test_updateUserByKeyValuesShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updateUserByKeyValues(self.DEFAULT_KEYVALUES)

        assert result == self.DEFAULT_REPOUPDATE_RESULT


class TestPostUpdateService:
    DEFAULT_REPOUPDATE_RESULT = 'default_result'
    DEFAULT_KEYVALUES = dict(
        postId='0',
        content='Hello this is my first post'
    )
    
    @pytest.fixture(scope='function', autouse=True)
    def setup_mocks(self, setup_service):
        mock_repo = setup_service._repo
        mock_repo.updatePost.return_value = self.DEFAULT_REPOUPDATE_RESULT

    def test_updatePostByKeyValuesShouldPassSearchFilterAndKeyValues(self, setup_service):
        mock_repo = setup_service._repo
        searchFilter = PrimitiveFilter.createFilter(dict(
            field='postId', operator='eq', value=[ self.DEFAULT_KEYVALUES['postId'] ]
        ))
        update = self.DEFAULT_KEYVALUES.copy().pop('postId')

        setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

        mock_repo.updatePost.assert_called_with(searchFilter, update)

    def test_updatePostByKeyValuesShouldRaiseExceptionWhenNoUserIdWasPassed(self, setup_service):
        keyValues = dict(content='Some post')

        with pytest.raises(exceptions.IdNotSpecifiedError):
            setup_service.updatePostByKeyValues(keyValues)

    def test_updatePostByKeyValuesShouldReturnResultFromRepo(self, setup_service):
        result = setup_service.updatePostByKeyValues(self.DEFAULT_KEYVALUES)

        assert result == self.DEFAULT_REPOUPDATE_RESULT
