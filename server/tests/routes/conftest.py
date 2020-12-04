# -*- coding: utf-8 -*-
"""
This file houses fixtures for routes
"""
import pytest

import tests.mocks as mocks

@pytest.fixture(scope='module')
def mockApp(app):
    """
    Replaces some objects in configuration by its mocked versions.
    
    Args:
        app: mocked application object found in fixture ../conftest.py
    Yields:
        the same application received as argument
    """
    mockDB = mocks.createMockRepo()
    app.config['DATABASE_REPOSITORY'] = mockDB

    mockCreate = mocks.createMockEntityCreationService()
    app.config['CREATION_SERVICE'] = mockCreate
    
    mockSearch = mocks.createMockSearchService()
    app.config['SEARCH_SERVICE'] = mockSearch

    mockUpdate = mocks.createMockUpdateService()
    app.config['UPDATE_SERVICE'] = mockUpdate

    mockDelete = mocks.createMockDeleteService()
    app.config['DELETE_SERVICE'] = mockDelete

    mockUserAuth = mocks.createMockUserAuth()
    app.config['AUTHENTICATION_SERVICE'] = mockUserAuth

    mockSessionUser = mocks.createMockRequestUserManager()
    mockSessionUser.addCurrentUserToResponse.side_effect = lambda response: response
    app.config['REQUESTUSER_MIDDLEWARE'] = mockSessionUser

    yield app


@pytest.fixture(scope='function')
def client(mockApp):
    """
    Creates a test client for the application.
    Test functions that uses this fixture would be executed inside an environment
    where the flask context persists.
    
    Args:
        mockApp: mocked application object returned from mockApp() fixture
    Yields:
        Client object
    """
    with mockApp.test_client() as client:
        yield client
