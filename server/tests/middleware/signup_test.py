# -*- coding: utf-8 -*-
"""
Unit test of signup.py
"""
import pytest

from server.middleware.signup import Signup
import tests.mocks as mocks
import server.exceptions as exceptions
from server.database.filter import Filter

@pytest.fixture(scope='function')
def mockDB(app):
    mockDB = mocks.createMockDB()
    app.config['DATABASE_OBJECT'] = mockDB

    yield mockDB

@pytest.fixture(scope='function')
def context(app):
    with app.app_context():
        yield

def test_signupCalls2CRUDMethods(context, saveOldConfig, mockDB):
    userProps = {
        'userName': 'tommy@myforumwebapp.com',
        'password': '12345678',
    }
    mockDB.searchUser.return_value = []

    Signup.signup(userProps)

    assert mockDB.searchUser.call_count == 1
    expectedFilter = [ Filter.createFilter({
        'field': 'userName',
        'operator': 'eq',
        'value': [ userProps['userName'] ],
    }) ]
    mockDB.searchUser.assert_called_with(expectedFilter)
    assert mockDB.createUser.call_count == 1
    mockDB.createUser.assert_called_with({ **userProps, 'displayName': 'tommy' })

def test_sigupRaisesExceptionWhenSearchUserReturnsUsers(context, saveOldConfig, mockDB):
    userProps = {
        'userName': 'tommy@myforumwebapp.com',
        'password': '12345678',
    }
    mockDB.searchUser.return_value = [ userProps ]

    with pytest.raises(exceptions.DuplicateUserError):
        Signup.signup(userProps)

    assert mockDB.createUser.call_count == 0

def test_signupPropagatesExceptionFromSearchUser(context, saveOldConfig, mockDB):
    userProps = {
        'userName': 'tommy@myforumwebapp.com',
        'password': '12345678',
    }
    exception = exceptions.ServerMiscError
    mockDB.searchUser.side_effect = exception()

    with pytest.raises(exception):
        Signup.signup(userProps)

def test_signupPropagatesExceptionFromCreateUser(context, saveOldConfig, mockDB):
    userProps = {
        'userName': 'tommy@myforumwebapp.com',
        'password': '12345678',
    }
    exception = exceptions.ServerMiscError
    mockDB.createUser.side_effect = exception()

    with pytest.raises(exception):
        Signup.signup(userProps)