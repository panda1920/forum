# -*- coding: utf-8 -*-
"""
This file houses tests for request_user.py
"""
import json
from unittest.mock import MagicMock

import pytest

import tests.mocks as mocks
from tests.helpers import create_mock_entity_fromattrs
import server.routes.route_utils as route_utils
from server import server
from server.middleware.request_user import RequestUserManager
from server.services.session import SessionService

DEFAULT_USER_ATTRS = {
    '_id': 'some_random_id',
    'userId': '1',
    'displayName': 'Bobby',
    'userName': 'Bobby',
    'password': '12345678',
}
DEFAULT_RESPONSE_DATA = {
    'someData': [ 1, 2, 3 ],
}


@pytest.fixture(scope='function')
def session_user():
    mock_user = create_mock_entity_fromattrs(DEFAULT_USER_ATTRS)
    mock_user.to_json.return_value = DEFAULT_USER_ATTRS
    mock_session = mocks.createMockSessionService()
    mock_session.get_user.return_value = mock_user
    mock_session.REQUEST_USER_KEY = SessionService.REQUEST_USER_KEY
    
    mock_context = mocks.createMockFlaskContext()

    return RequestUserManager(mock_session, mock_context)


def createMockResponse():
    mock_response = MagicMock()
    mock_response.get_data.return_value = json.dumps(DEFAULT_RESPONSE_DATA)

    return mock_response


class TestRequestUserManager:
    def test_setCurrentUserShouldCallPopulateRequestUserOnSession(self, session_user):
        mock_session = session_user._session

        session_user.setCurrentUser()

        assert mock_session.populate_request_user.call_count == 1

    def test_addCurrentUserToResponseShouldRetrieveUserInfoFromRequestContext(self, session_user):
        mock_session = session_user._session
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        assert mock_session.get_user.call_count == 1

    def test_addCurrentUserToResponseShouldCallToJsonOnRequestContextUser(self, session_user):
        mock_user = session_user._session.get_user.return_value
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        assert mock_user.to_json.call_count == 1

    def test_addCurrentUserToResponseShouldUpdateDataWithRequestContextUser(self, session_user):
        mock_response = createMockResponse()

        session_user.addCurrentUserToResponse(mock_response)

        mock_response.set_data.assert_called()
        data_string, *_ = mock_response.set_data.call_args[0]
        updated_data = json.loads(data_string)

        assert SessionService.REQUEST_USER_KEY in updated_data
        for k, v in DEFAULT_RESPONSE_DATA.items():
            assert updated_data[k] == v
        for k, v in DEFAULT_USER_ATTRS.items():
            assert updated_data[SessionService.REQUEST_USER_KEY][k] == v


class TestRequestUserManagerAgainstRoute:
    @pytest.fixture(scope='function')
    def app(self):
        app = server.setupApp()
        app.testing = True
        yield app
    
    def test_requestWithSetCurrentUserShouldCallPopulateRequestUser(self, session_user, app):
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
            assert mock_session.populate_request_user.call_count == 1

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

            assert SessionService.REQUEST_USER_KEY in responseJson
            for k, v in DEFAULT_RESPONSE_DATA.items():
                assert responseJson[k] == v
            for k, v in DEFAULT_USER_ATTRS.items():
                assert responseJson[SessionService.REQUEST_USER_KEY][k] == v
