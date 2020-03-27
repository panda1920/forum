# -*- coding: utf-8 -*-
"""
This file houses tests for session.py
"""
import pytest

import tests.mocks as mocks

from server.services.session import SessionService
from server.database.filter import PrimitiveFilter

DEFAULT_USER = {
    '_id': 'some_random_id',
    'userId': '1',
    'displayName': 'Bobby',
    'userName': 'Bobby',
    'password': '12345678',
}

FILTERED_USER = {
    # '_id'
    'userId': '1',
    'displayName': 'Bobby',
    'userName': 'Bobby',
    # 'password': '12345678',
}


@pytest.fixture(scope='function')
def session_user():
    mock_context = mocks.createMockFlaskContext()

    mock_repo = mocks.createMockDB()
    mock_repo.searchUser.return_value = dict(
        users=[ DEFAULT_USER ],
        returnCount=1,
        matchCount=1,
    )

    return SessionService(mock_repo, mock_context)


class TestSessionService:
    def test_setSessionUserShouldPutUserInSession(self, session_user):
        mock_context = session_user._context

        session_user.set_user(DEFAULT_USER)

        mock_context.write_session.assert_called_with(
            SessionService.SESSION_USER_KEY,
            dict(userId=DEFAULT_USER['userId'])
        )

    def test_setSessionSUserShouldSearchUserFromRepo(self, session_user):
        mock_repo = session_user._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ DEFAULT_USER['userId'] ]
        ))

        session_user.set_user(DEFAULT_USER)

        mock_repo.searchUser.assert_called_once()
        mock_repo.searchUser.assert_called_with(expectedFilter)

    def test_setSessionUserShouldPutUserInGlobal(self, session_user):
        mock_context = session_user._context

        session_user.set_user(DEFAULT_USER)

        mock_context.write_global.assert_called_with(
            SessionService.SESSION_USER_KEY,
            FILTERED_USER
        )

    def test_removeSessionUserShouldSearchAnonymousUserFromRepo(self, session_user):
        mock_repo = session_user._repo
        expectedFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ SessionService.ANONYMOUS_USER['userId'] ]
        ))

        session_user.remove_user()

        mock_repo.searchUser.assert_called_once()
        mock_repo.searchUser.assert_called_with(expectedFilter)

    def test_removeSessionUserShouldPutAnonymousUserInSession(self, session_user):
        mock_context = session_user._context
        anonymous_user_indb = dict(userId='0', userName='anonymous@myforumwebapp.com')
        mock_repo = session_user._repo
        mock_repo.searchUser.return_value = dict(
            users=[ anonymous_user_indb ],
            returnCount=1,
            matchedCount=1,
        )

        session_user.remove_user()

        mock_context.write_session.assert_called_with(
            SessionService.SESSION_USER_KEY,
            SessionService.ANONYMOUS_USER,
        )

    def test_removeSessionUserShouldWriteToGlobal(self, session_user):
        mock_context = session_user._context
        anonymous_user_indb = dict(userId='0', userName='anonymous@myforumwebapp.com')
        mock_repo = session_user._repo
        mock_repo.searchUser.return_value = dict(
            users=[ anonymous_user_indb ],
            returnCount=1,
            matchedCount=1,
        )

        session_user.remove_user()

        mock_context.write_global.assert_called_with(
            SessionService.SESSION_USER_KEY,
            anonymous_user_indb,
        )
