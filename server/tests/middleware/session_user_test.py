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
ANONYMOUS_USER = dict(userId='0')
SESSION_USER_KEY = 'sessionUser'


@pytest.fixture(scope='function')
def session_user():
    mock_session = mocks.createMockSessionService()
    mock_session.ANONYMOUS_USER = ANONYMOUS_USER
    mock_session.SESSION_USER_KEY = SESSION_USER_KEY

    mock_context = mocks.createMockFlaskContext()
    mock_context.read_session.return_value = DEFAULT_SESSION_USERINFO
    mock_context.read_global.return_value = FILTERED_USER

    return SessionUserManager(mock_session, mock_context)


def createMockResponse():
    mock_response = MagicMock()
    mock_response.get_data.return_value = json.dumps(DEFAULT_RESPONSE_DATA)

    return mock_response


class TestSessionUserManager:
    def test_setCurrentUserShouldRetrieveUserFromSession(self, session_user):
        mock_context = session_user._context

        session_user.setCurrentUser()

        mock_context.read_session.assert_called_with(SESSION_USER_KEY)

    def test_setCurrentUserShouldPassSessionUserToService(self, session_user):
        mock_session = session_user._session

        session_user.setCurrentUser()

        mock_session.set_global_user.assert_called_with(DEFAULT_SESSION_USERINFO)

    def test_setCurrentUserShouldPassAnonymousUserWhenNoSessionInfo(self, session_user):
        mock_context = session_user._context
        mock_context.read_session.return_value = None
        mock_session = session_user._session

        session_user.setCurrentUser()

        mock_session.set_global_user.assert_called_with(ANONYMOUS_USER)

    def test_addCurrentUserToResponseShouldRetrieveUserInfoFromGlobal(self, session_user):
        mock_context = session_user._context
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        mock_context.read_global.assert_called_with(SESSION_USER_KEY)

    def test_addCurrentUserToResponseShouldPlaceRetrievedUserInfoInResponse(self, session_user):
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        mock_response.get_data.assert_called()
        data_set, *_ = mock_response.set_data.call_args[0]
        assert json.loads(data_set) == {
            **DEFAULT_RESPONSE_DATA,
            SESSION_USER_KEY: FILTERED_USER
        }


class TestSessionUserManagerAgainstRoute:
    @pytest.fixture(scope='function')
    def app(self):
        app = server.setupApp()
        app.testing = True
        yield app
    
    def test_requestWithSetCurrentUserShouldPassSessionUserToService(self, session_user, app):
        mock_session = session_user._session
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
            mock_session.set_global_user.assert_called_with(DEFAULT_SESSION_USERINFO)

    def test_requestWithSetCurrentUserShouldPassAnonymousUserWhenNoInfo(self, session_user, app):
        mock_session = session_user._session
        mock_context = session_user._context
        mock_context.read_session.return_value = None
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
            mock_session.set_global_user.assert_called_with(ANONYMOUS_USER)
        
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
                SESSION_USER_KEY: FILTERED_USER,
            }
