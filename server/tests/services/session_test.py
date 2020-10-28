# -*- coding: utf-8 -*-
"""
This file houses tests for session.py
"""
import pytest

import tests.mocks as mocks
from tests.helpers import create_mock_entity_fromattrs
from server.services.session import SessionService
from server.database.filter import PrimitiveFilter

DEFAULT_USER = create_mock_entity_fromattrs({
    '_id': 'some_random_id',
    'userId': '1',
    'displayName': 'Bobby',
    'userName': 'Bobby',
    'password': '12345678',
})

ANONYMOUS_USER = create_mock_entity_fromattrs({
    'userId': SessionService.ANONYMOUS_USERID
})


@pytest.fixture(scope='function')
def session_service():
    mock_context = mocks.createMockFlaskContext()

    mock_repo = mocks.createMockRepo()
    mock_repo.searchUser.return_value = dict(
        users=[ ANONYMOUS_USER ],
        returnCount=1,
        matchCount=1,
    )

    return SessionService(mock_repo, mock_context)


class TestSessionService:
    def test_setSessionUserShouldPutUserIdInSession(self, session_service):
        mock_context = session_service._context

        session_service.set_user(DEFAULT_USER)

        mock_context.write_session.assert_called_with(
            SessionService.SESSION_USER_KEY,
            DEFAULT_USER.userId,
        )

    def test_setSessionUserShouldPutUserInGlobal(self, session_service):
        mock_context = session_service._context

        session_service.set_user(DEFAULT_USER)

        mock_context.write_global.assert_called_with(
            SessionService.REQUEST_USER_KEY,
            DEFAULT_USER
        )

    def test_removeSessionUserShouldSearchForAnonymousUser(self, session_service):
        mock_repo = session_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ SessionService.ANONYMOUS_USERID ]
        ))

        session_service.remove_user()

        search_filter, *_ = mock_repo.searchUser.call_args_list[0][0]
        assert search_filter == expected_filter

    def test_removeSessionUserShouldPutAnonymousUserInSession(self, session_service):
        mock_context = session_service._context

        session_service.remove_user()

        mock_context.write_session.assert_called_with(
            SessionService.SESSION_USER_KEY,
            ANONYMOUS_USER.userId,
        )

    def test_removeSessionUserShouldWriteToGlobal(self, session_service):
        mock_context = session_service._context

        session_service.remove_user()

        mock_context.write_global.assert_called_with(
            SessionService.REQUEST_USER_KEY,
            ANONYMOUS_USER,
        )

    def test_getUserShouldReadFromGlobalUsingSessionUserKey(self, session_service):
        mock_context = session_service._context

        session_service.get_user()

        mock_context.read_global.assert_called_with(SessionService.REQUEST_USER_KEY)

    def test_getUserShouldReturnWhatsReturnedFromContext(self, session_service):
        mock_context = session_service._context
        session_user = create_mock_entity_fromattrs({ 'userId': 'test_user_333 '})
        mock_context.read_global.return_value = session_user

        result = session_service.get_user()

        assert result == session_user

    def test_populate_request_userShouldSearchForUserBySessionUserId(self, session_service):
        userid = 'test_userid'
        context = session_service._context
        context.read_session.return_value = userid
        repo = session_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ userid ],
        ))

        session_service.populate_request_user()

        repo.searchUser.assert_called_with(expected_filter)

    def test_populate_request_userShouldSearchForAnonymousUserIfNoSessionUser(self, session_service):
        context = session_service._context
        context.read_session.return_value = None
        repo = session_service._repo
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ SessionService.ANONYMOUS_USERID ],
        ))

        session_service.populate_request_user()

        repo.searchUser.assert_called_with(expected_filter)

    def test_populate_request_userShouldPutFoundUserInGlobalContext(self, session_service):
        context = session_service._context
        repo = session_service._repo
        user_from_repo = create_mock_entity_fromattrs( dict(userId='test_session_user') )
        repo.searchUser.return_value = { 'users': [ user_from_repo ], }

        session_service.populate_request_user()

        context.write_global.assert_called_with(
            SessionService.REQUEST_USER_KEY,
            user_from_repo,
        )
