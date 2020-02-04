# -*- coding: utf-8 -*-
"""
This file houses tests for entity_creation_service.py
"""

import pytest
from unittest.mock import ANY

import tests.mocks as mocks
from server.services.entity_creation_service import EntityCreationService

@pytest.fixture(scope='function')
def service():
    mockDB = mocks.createMockDB()
    yield EntityCreationService(mockDB)

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