# -*- coding: utf-8 -*-
"""
This file houses tests for session.py
"""
import pytest

from flask import g, session

import tests.mocks as mocks
from server.middleware.session import SessionManager

class TestSessionManager:
    TEST_USER = {
        'userId': '1',
        'displayName': 'Bobby',
        'userName': 'Bobby',
        'password': '12345678',
    }

    def test_setCurrentUserFromSessionPutsSessionUserInGlobal(self):
        mockSession = mocks.createMockSession({
            'userId': self.TEST_USER['userId'],
        })
        mockGlobal = mocks.createMockG()
        mockGlobal.currentUser = None

        SessionManager.setCurrentUserFromSession(mockGlobal, mockSession)

        assert mockGlobal.currentUser == { 'userId': self.TEST_USER['userId'] }

    def test_setCurrentUserFromSessionPutsAnonymousUserInGlobalWhenNoUserInfo(self):
        mockSession = mocks.createMockSession()
        mockGlobal = mocks.createMockG()
        mockGlobal.currentUser = None
        
        SessionManager.setCurrentUserFromSession(mockGlobal, mockSession)

        assert mockGlobal.currentUser == { 'userId': '0' }

    def test_setCurrentUserFromSessionPutsAnonymousUserInSessionWhenNoUserInfo(self):
        mockSession = mocks.createMockSession()
        mockGlobal = mocks.createMockG()
        mockGlobal.currentUser = None
        
        SessionManager.setCurrentUserFromSession(mockGlobal, mockSession)

        assert 'userId' in mockSession
        assert mockSession['userId'] == '0'

    def test_setSessionUserPutsUserInSession(self, app):
        with app.test_request_context():
            SessionManager.setSessionUser(self.TEST_USER)

            assert session['userId'] == self.TEST_USER['userId']

    def test_setSessionUserPutsUserInGlobal(self, app):
        with app.test_request_context():
            SessionManager.setSessionUser(self.TEST_USER)

            assert g.currentUser['userId'] == self.TEST_USER['userId']
