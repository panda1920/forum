import pytest
from contextlib import contextmanager

from server import server
import tests.mocks as mocks
import server.exceptions as exceptions
from server.database import database
from server.database.filter import Filter
from server.middleware.session import SessionManager as session
    
class Test_authenticateUserDecorator:
    TEST_USER = {
        'userId': '1',
        'displayName': 'Bobby',
        'userName': 'Bobby',
        'password': '12345678',
    }
    def test_setCurrentUserFromSessionPutsSessionUserInGlobal(self, app):
        mockSession = mocks.createMockSession({
            'userId': self.TEST_USER['userId'],
        })
        mockGlobal = mocks.createMockG()
        mockGlobal.currentUser = None

        session.setCurrentUserFromSession(mockGlobal, mockSession)

        assert mockGlobal.currentUser == { 'userId': self.TEST_USER['userId'] }

    def test_setCurrentUserFromSessionPutsAnonymousUserInGlobalWhenNoUserInfo(self, app):
        mockSession = mocks.createMockSession()
        mockGlobal = mocks.createMockG()
        mockGlobal.currentUser = None
        
        session.setCurrentUserFromSession(mockGlobal, mockSession)

        assert mockGlobal.currentUser == { 'userId': '0' }

    def test_setCurrentUserFromSessionPutsAnonymousUserInSessionWhenNoUserInfo(self, app):
        mockSession = mocks.createMockSession()
        mockGlobal = mocks.createMockG()
        mockGlobal.currentUser = None
        
        session.setCurrentUserFromSession(mockGlobal, mockSession)

        assert 'userId' in mockSession
        assert mockSession['userId'] == '0'