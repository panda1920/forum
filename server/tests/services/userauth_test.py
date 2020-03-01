# -*- coding: utf-8 -*-
"""
This file houses tests for userauth.py
"""

import pytest

import server.exceptions as exceptions
from server.services.userauth import UserAuthentication
from server.database.filter import PrimitiveFilter
from tests.mocks import createMockDB, createMockSessionManager


@pytest.fixture(scope='function')
def user_auth():
    repo = createMockDB()
    session = createMockSessionManager()
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


# class TestToken:
#     TEST_SECRET = 'my_secret_key'
#     TEST_PAYLOAD = dict(userId='1111')
#     @pytest.fixture(scope='function', autouse=True)
#     def setup_testenv(self):
#         default_environ = os.environ
#         os.environ['JWT_SECRET_KEY'] = self.TEST_SECRET
#         yield
#         os.environ = default_environ

#     # token creation
#     # data inside
#     # token authorization by date
#     # token authorization by userId
#     def test_createTokenCreatesTokenWithRequiredPayload(self, user_auth):
#         payload = self.TEST_PAYLOAD
        
#         token = user_auth.createToken(payload)

#     def test_validateTokenShouldRaiseExceptionWhenIatExpired(self):
#         pass

#     def test_validateTokenShouldRaiseExceptionWhenWrongSecret(self):
#         pass

#     def test_validateTokenShouldPassWhenIatIsWithinBounds(self):
#         pass

#     def test_authorizeTokenShouldRaiseExceptionWhenUserIdDoesNotMatch(self):
#         pass

class TestLogin:
    DEFAULT_USER_CREDENTIALS = dict(
        userName='bobby@myforumwebapp.com',
        password='password'
    )
    DEFAULT_USER_IN_REPO = dict(
        userId='000',
        userName='bobby@myforumwebapp.com',
        password='$pbkdf2-sha256$29000$6z0nxLh37v3fOydkjBHi3A$51waSF7m1N5sFyz/b9wfd6pcuWu4l0T1VceK3WcxJxI'
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

    def test_loginShouldSetUserValueOnSession(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        user_auth.login(credentials)

        mockSession = user_auth._session
        mockSession.setSessionUser.assert_called_once_with(self.DEFAULT_USER_IN_REPO)

    def test_loginUserShouldReturnUserInfoWhenSuccessful(self, user_auth):
        credentials = self.DEFAULT_USER_CREDENTIALS
        mockRepo = user_auth._repo
        mockRepo.searchUser.return_value = dict(
            returnCount=0, matchedCount=0, users=[ self.DEFAULT_USER_IN_REPO ]
        )

        user = user_auth.login(credentials)
        assert user == self.DEFAULT_USER_IN_REPO

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
