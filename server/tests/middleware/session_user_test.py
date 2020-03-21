# -*- coding: utf-8 -*-
"""
This file houses tests for session_user.py
"""
import json
from unittest.mock import MagicMock

import pytest

import tests.mocks as mocks
import server.routes.route_utils as route_utils
from server import server
from server.middleware.session_user import SessionUserManager

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

DEFAULT_SESSION_USERINFO = {
    'userId': '1',
}

DEFAULT_RESPONSE_DATA = {
    'someData': [ 1, 2, 3 ],
}


@pytest.fixture(scope='function')
def session_user():
    mock_context = mocks.createMockFlaskContext()
    mock_context.read_session.return_value = DEFAULT_SESSION_USERINFO
    mock_context.read_global.return_value = DEFAULT_USER

    mock_search = mocks.createMockSearchService()
    mock_search.searchUsersByKeyValues.return_value = dict(
        users=[ DEFAULT_USER ],
        returnCount=1,
        matchCount=1,
    )

    return SessionUserManager(mock_search, mock_context)


def createMockResponse():
    mock_response = MagicMock()
    mock_response.get_data.return_value = json.dumps(DEFAULT_RESPONSE_DATA)

    return mock_response


class TestSessionUserManager:
    def test_setCurrentUserShouldRetrieveUserFromContext(self, session_user):
        mock_context = session_user._context

        session_user.setCurrentUser()

        mock_context.read_session.assert_called_with(SessionUserManager.SESSION_USER_KEY)

    def test_setCurrentUserShouldSearchSessionUser(self, session_user):
        mock_search = session_user._search

        session_user.setCurrentUser()

        mock_search.searchUsersByKeyValues.assert_called_with(
            dict(userId=DEFAULT_SESSION_USERINFO['userId'])
        )

    def test_setCurrentUserShouldPutFilteredSearchedInformationOnGlobal(self, session_user):
        mock_context = session_user._context

        session_user.setCurrentUser()

        mock_context.write_global.assert_called_with(
            SessionUserManager.SESSION_USER_KEY,
            FILTERED_USER
        )

    def test_setCurrentUserShouldSearchAnonymousUserWhenNoSessionInfo(self, session_user):
        mock_context = session_user._context
        mock_context.read_session.return_value = None
        mock_search = session_user._search

        session_user.setCurrentUser()

        mock_search.searchUsersByKeyValues.assert_called_with(
            dict(userId='0')
        )

    def test_setSessionUserShouldPutUserInSession(self, session_user):
        mock_context = session_user._context

        session_user.setSessionUser(DEFAULT_USER)

        mock_context.write_session.assert_called_with(
            SessionUserManager.SESSION_USER_KEY,
            dict(userId=DEFAULT_USER['userId'])
        )

    def test_setSessionUserShouldPutUserInGlobal(self, session_user):
        mock_context = session_user._context

        session_user.setSessionUser(DEFAULT_USER)

        mock_context.write_global.assert_called_with(
            SessionUserManager.SESSION_USER_KEY,
            FILTERED_USER
        )

    def test_removeSessionUserShouldPutAnonymousUserInSession(self, session_user):
        mock_context = session_user._context

        session_user.removeSessionUser()

        mock_context.write_session.assert_called_with(
            SessionUserManager.SESSION_USER_KEY,
            SessionUserManager.ANONYMOUS_USER,
        )

    def test_removeSessionUserShouldWriteToGlobal(self, session_user):
        mock_context = session_user._context
        anonymous_user_indb = dict(userId='0', userName='anonymous@myforumwebapp.com')
        mock_search = session_user._search
        mock_search.searchUsersByKeyValues.return_value = dict(
            users=[ anonymous_user_indb ],
            returnCount=0,
            matchedCount=0,
        )

        session_user.removeSessionUser()

        mock_context.write_global.assert_called_with(
            SessionUserManager.SESSION_USER_KEY,
            anonymous_user_indb,
        )

    def test_addCurrentUserToResponseShouldRetrieveUserInfoFromGlobal(self, session_user):
        mock_context = session_user._context
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        mock_context.read_global.assert_called_with(SessionUserManager.SESSION_USER_KEY)

    def test_addCurrentUserToResponseShouldPlaceRetrievedUserInfoInResponse(self, session_user):
        mock_response = MagicMock()
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        mock_response.get_data.assert_called()
        data_set, *_ = mock_response.set_data.call_args[0]
        assert json.loads(data_set) == {
            **DEFAULT_RESPONSE_DATA,
            SessionUserManager.SESSION_USER_KEY: DEFAULT_USER
        }


class TestSessionUserManagerAgainstRoute:
    @pytest.fixture(scope='function')
    def app(self):
        app = server.setupApp()
        app.testing = True
        yield app
    
    def test_requestWithSetCurrentUserShouldHaveDefaultUserInGlobal(self, session_user, app):
        mock_context = session_user._context
        path = '/test-route'

        @app.route(path, methods=['GET'])
        def some_route():
            return route_utils.createJSONResponse([], 200)

        @app.before_request
        def setuser():
            session_user.setCurrentUser()

        with app.test_client() as client:
            response = client.get(path)

            assert response.status_code == 200
            mock_context.write_global.assert_called_with(SessionUserManager.SESSION_USER_KEY, FILTERED_USER)
        
    def test_requestWithaddCurrentUserToResponseShouldHaveDefaultUserInResponse(self, session_user, app):
        path = '/test-route'

        @app.route(path, methods=['GET'])
        def some_route():
            return route_utils.createJSONResponse([ DEFAULT_RESPONSE_DATA ], 200)

        @app.after_request
        def setuser(response):
            session_user.addCurrentUserToResponse(response)
            return response

        with app.test_client() as client:
            response = client.get(path)

            assert response.status_code == 200
            responseJson = response.get_json()
            assert responseJson == {
                **DEFAULT_RESPONSE_DATA,
                SessionUserManager.SESSION_USER_KEY: DEFAULT_USER,
            }
