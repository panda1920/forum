# -*- coding: utf-8 -*-
"""
This file houses tests for userauth.py
"""

import pytest

import server.exceptions as exceptions
from server.services.userauth import UserAuthentication
from server.database.filter import PrimitiveFilter
from tests.mocks import createMockDB, createMockSessionUserManager


@pytest.fixture(scope='function')
def user_auth():
    repo = createMockDB()
    session = createMockSessionUserManager()
    return UserAuthentication(repo, PrimitiveFilter, session)
    

class TestPasswordHashing:
    DEFAULT_PASSWORD = 'password'
    # pre-generated hash for above password using the same context in UserAuthentication
    DEFAULT_HASHED = '$pbkdf2-sha256$29000$6z0nxLh37v3fOydkjBHi3A$51waSF7m1N5sFyz/b9wfd6pcuWu4l0T1VceK3WcxJxI'
    # pre-generated hash for above password using different context
    DIF_CONTEXT_HASHED = '$2b$12$m/c3kTn0DzeBAGAnUDqh3.yICIZAnQyqVB62aO6n9pLpW2uRsVVOa'

    def test_passwordHashingOfDefaultPasswordYieldsHashedString(self, user_auth):
        hashed = user_auth.hashPassword(self.DEFAULT_PASSWORD)
        
        assert hashed is not None
        assert type(hashed) is str
        assert hashed != self.DEFAULT_PASSWORD
        assert hashed != self.DEFAULT_HASHED

    def test_passwordVerificationPassesAgainstDefaultPasswordAndDefaultHash(self, user_auth):
        assert user_auth.verifyPassword(self.DEFAULT_PASSWORD, self.DEFAULT_HASHED)

    def test_passwordVeriicationPassesAgainstDefaultPasswordAndGeneratedHash(self, user_auth):
        hashed = user_auth.hashPassword(self.DEFAULT_PASSWORD)
        assert user_auth.verifyPassword(self.DEFAULT_PASSWORD, hashed)

    def test_passwordVerificationFailsAgainstWrongPasswordAndDefaultHash(self, user_auth):
        password = 'wrong_password'
        assert not user_auth.verifyPassword(password, self.DEFAULT_HASHED)

    def test_passwordVerificationFailsAgainstHashGeneratedByDifferentContext(self, user_auth):
        assert not user_auth.verifyPassword(self.DEFAULT_PASSWORD, self.DIF_CONTEXT_HASHED)


class TestLogin:
    DEFAULT_USER_CREDENTIALS = dict(
        userName='bobby@myforumwebapp.com',
        password='password'
    )
    DEFAULT_USER_IN_REPO = dict(
        _id='some_random_id',
        userId='000',
        userName='bobby@myforumwebapp.com',
        password='$pbkdf2-sha256$29000$6z0nxLh37v3fOydkjBHi3A$51waSF7m1N5sFyz/b9wfd6pcuWu4l0T1VceK3WcxJxI',
    )

    def test_loginShouldCallSearchUserOnRepo(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        user_auth.login(credentials)

        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userName', operator='eq', value=[ credentials['userName'] ]
        ))
        mockRepo.searchUser.assert_called_once_with(expectedFilter)

    def test_loginShouldSetSearchedUserInfoOnSession(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        mockSession = user_auth._session
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        user_auth.login(credentials)

        mockSession.setSessionUser.assert_called_once_with(self.DEFAULT_USER_IN_REPO)

    def test_loginUserShouldReturnNoneWhenSuccessful(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        rv = user_auth.login(credentials)
        assert rv is None

    def test_loginShouldRaiseExceptionWhenUserNotFound(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[]
        )

        with pytest.raises(exceptions.InvalidUserCredentials):
            user_auth.login(credentials)

    def test_loginShouldRaiseExceptionWhenWrongPassword(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        credentials['password'] = 'some_random_string'
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        with pytest.raises(exceptions.InvalidUserCredentials):
            user_auth.login(credentials)

    def test_loginShouldRaiseExceptionWhenInvalidCredentials(self, user_auth):
        credentialsList = [
            dict(userName='', password='password'),
            dict(userName=None, password='password'),
            dict(userName='bobby@myforumwebapp.com', password=None),
            dict(userName='', password=''),
        ]
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        for credentials in credentialsList:
            with pytest.raises(exceptions.InvalidUserCredentials):
                user_auth.login(credentials)


class TestLogout:
    def test_logoutShouldCallRemoveSessionUser(self, user_auth):
        mockSession = user_auth._session

        user_auth.logout()

        mockSession.removeSessionUser.assert_called_once()
