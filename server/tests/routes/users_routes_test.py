# -*- coding: utf-8 -*-
"""
This file houses tests for User related routes available for this app
"""
import json
import pytest

from server.config import Config
from server.entity import User
from tests.helpers import create_mock_entities
import server.exceptions as exceptions


DEFAULT_RETURN_SEARCHUSER_ATTRSET = [
    dict(userId='test_userid1', userName='user1@example.com', displayName='alice'),
    dict(userId='test_userid2', userName='user2@example.com', displayName='bobby'),
    dict(userId='test_userid3', userName='user3@example.com', displayName='charlie'),
]
DEFAULT_RETURN_SIGNUP = dict(created='user')
DEFAULT_RETURN_UPDATEUSER = 'some_value_updateuser'
DEFAULT_RETURN_DELETEUSER = dict(deleteCount=1)
DEFAULT_RETURN_LOGIN = dict()
DEFAULT_RETURN_LOGOUT = dict()


@pytest.fixture(scope='function', autouse=True)
def set_mock_returnvalues(mockApp):
    Config.getCreationService(mockApp).signup.return_value = DEFAULT_RETURN_SIGNUP
    
    mock_returned_users = create_mock_entities(DEFAULT_RETURN_SEARCHUSER_ATTRSET)
    for user, attrs in zip(mock_returned_users, DEFAULT_RETURN_SEARCHUSER_ATTRSET):
        user.to_serialize.return_value = attrs
    Config.getSearchService(mockApp).searchUsersByKeyValues.return_value = dict(users=mock_returned_users)

    Config.getUpdateService(mockApp).updateUser.return_value = DEFAULT_RETURN_UPDATEUSER

    Config.getDeleteService(mockApp).deleteUserById.return_value = DEFAULT_RETURN_DELETEUSER

    Config.getAuthService(mockApp).login.return_value = DEFAULT_RETURN_LOGIN
    Config.getAuthService(mockApp).logout.return_value = DEFAULT_RETURN_LOGOUT


class TestUserAPIs:
    USERAPI_BASE_URL = '/v1/users'

    def test_searchUsersPassesQueryStringToService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='username'
        )

        with mockApp.test_client() as client:
            client.get(self.USERAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchUsersByKeyValues.assert_called_with(keyValues)

    def test_searchUsersAPICalls_to_serializeOnReturnedEntities(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        mock_users = mockSearch.searchUsersByKeyValues.return_value['users']
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            client.get(self.USERAPI_BASE_URL, query_string=keyValues)

            for user in mock_users:
                assert (user.to_serialize.call_count) == 1

    def test_searchUsersAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=keyValues)

            assert response.status_code == 200
            users = response.get_json()['result']['users']
            for user in users:
                assert user in DEFAULT_RETURN_SEARCHUSER_ATTRSET
        
    def test_searchUsersReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='username'
        )
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError,
            exceptions.InvalidFilterOperatorError,
        ]

        for e in exceptionsToTest:
            mockSearch.searchUsersByKeyValues.side_effect = e()
            with mockApp.test_client() as client:
                response = client.get(self.USERAPI_BASE_URL, query_string=keyValues)

                assert response.status_code == e.getStatusCode()

    def test_searchUserByExplicitIDPassesUserIdToService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            client.get(url)

            mockSearch.searchUsersByKeyValues.assert_called_with(dict(userId=userId))

    def test_searchUserByExplicitIDIgnoresQueryString(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'
        keyValues = dict(offset=30, limit=100)

        with mockApp.test_client() as client:
            client.get(url, query_string=keyValues)

            mockSearch.searchUsersByKeyValues.assert_called_with(dict(userId=userId))

    def test_searchUserByExplicitIDCalls_to_serializeOnReturnedEntities(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        mock_users = mockSearch.searchUsersByKeyValues.return_value['users']
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            client.get(url)

            for user in mock_users:
                assert (user.to_serialize.call_count) == 1

    def test_searchUserByExplicitIDReturns200AndWhatsReturnedFromService(self, mockApp):
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200
            users = response.get_json()['result']['users']
            for user in users:
                assert user in DEFAULT_RETURN_SEARCHUSER_ATTRSET

    def test_searchUserByExplicitIDReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError,
            exceptions.InvalidFilterOperatorError,
        ]

        for e in exceptionsToTest:
            mockSearch.searchUsersByKeyValues.side_effect = e()
            with mockApp.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createUserPassesUserEntityaToService(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
            'password': '12345678'
        }
        url = f'{self.USERAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            client.post(url, json=userProperties)

            passed_user, *_ = mockCreate.signup.call_args_list[0][0]
            assert isinstance(passed_user, User)
            for k, v in userProperties.items():
                assert getattr(passed_user, k) == v

    def test_createUserReturns201AndResultFromServiceWhenSuccess(self, mockApp):
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
            'password': '12345678'
        }
        url = f'{self.USERAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            response = client.post(url, json=userProperties)

            assert response.status_code == 201
            response_json = response.get_json()
            assert response_json['result'] == DEFAULT_RETURN_SIGNUP

    def test_createUserReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
            'password': '12345678'
        }
        url = f'{self.USERAPI_BASE_URL}/create'
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError,
            exceptions.InvalidFilterOperatorError,
        ]

        for e in exceptionsToTest:
            mockCreate.signup.side_effect = e()
            with mockApp.test_client() as client:
                response = client.post(url, json=userProperties)

                assert response.status_code == e.getStatusCode()

    def test_updateUserShouldPassUserEntityToServiceAndReturn200(self, client, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        userProperties = {
            'displayName': 'Jimmy',
        }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'

        response = client.patch(url, json=userProperties)

        assert response.status_code == 200
        passed_user, *_ = mockUpdate.updateUser.call_args_list[0][0]
        assert isinstance(passed_user, User)
        for k, v in userProperties.items():
            assert getattr(passed_user, k) == v
        assert response.get_json()['result'] == DEFAULT_RETURN_UPDATEUSER

    def test_updateUserReturnsErrorWhenNonJsonPassed(self, client, mockApp):
        requestDataToTest = 'some_random_string'
        headerToTest = { 'Content-Type': 'text/plain' }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'

        response = client.patch(url, data=requestDataToTest, headers=headerToTest)

        assert response.status_code == 400

    def test_updateUserReturnsErrorWhenUpdateUserRaisesException(self, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        userProperties = {
            'displayName': 'Jimmy',
        }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'
        exceptionsToTest = [
            exceptions.EntityValidationError('some error'),
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            mockUpdate.updateUser.side_effect = e
            with mockApp.test_client() as client:
                response = client.patch(url, json=userProperties)

            assert response.status_code == e.getStatusCode()

    def test_deleteUserByIdShouldPassUserIdToDeleteService(self, mockApp):
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'
        mockDelete = Config.getDeleteService(mockApp)

        with mockApp.test_client() as client:
            client.delete(url)

            mockDelete.deleteUserById.assert_called_with(userIdToDelete)

    def test_deleteUserByIdShouldReturn200AndReturnValueFromService(self, mockApp):
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200
            responseJson = response.get_json()
            responseJson['result'] == DEFAULT_RETURN_DELETEUSER

    def test_deleteUserReturnsErrorWhenDeleteUserRaisesException(self, mockApp):
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]
        mockDelete = Config.getDeleteService(mockApp)

        for e in exceptionsToTest:
            mockDelete.deleteUserById.side_effect = e
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()

    def test_loginShouldPassCredentialsToService(self, mockApp, client):
        userCredentials = dict(
            userName='Bobby',
            password='password',
        )
        url = f'{self.USERAPI_BASE_URL}/login'

        response = client.post(url, json=userCredentials)

        userauth = Config.getAuthService(mockApp)
        assert response.status_code == 200
        assert userauth.login.call_count == 1
        userauth.login.assert_called_with(userCredentials)

    def test_loginShouldReturn200AndResultFromServiceOnSuccess(self, mockApp, client):
        userCredentials = dict(
            userName='Bobby',
            password='password',
        )
        url = f'{self.USERAPI_BASE_URL}/login'

        response = client.post(url, json=userCredentials)

        assert response.status_code == 200
        data = response.get_json()
        assert data['result'] == DEFAULT_RETURN_LOGIN

    def test_loginShouldReturnErrorWhenLoginRaisesException(self, mockApp):
        userCredentials = dict(
            userName='Bobby',
            password='password',
        )
        url = f'{self.USERAPI_BASE_URL}/login'
        userauth = Config.getAuthService(mockApp)
        exceptionsToTest = [
            exceptions.InvalidUserCredentials,
            exceptions.ServerMiscError,
        ]

        for e in exceptionsToTest:
            userauth.login.side_effect = e('Some error string')
            with mockApp.test_client() as client:
                
                response = client.post(url, json=userCredentials)

                assert response.status_code == e.getStatusCode()

    def test_logoutShouldCallLogoutService(self, mockApp, client):
        url = f'{self.USERAPI_BASE_URL}/logout'
        userauth = Config.getAuthService(mockApp)

        client.post(url)

        userauth.logout.assert_called_once()

    def test_logoutShouldReturn200AndResultFromService(self, mockApp, client):
        url = f'{self.USERAPI_BASE_URL}/logout'

        response = client.post(url)

        assert response.status_code == 200
        assert response.get_json()['result'] == DEFAULT_RETURN_LOGOUT

    def test_logoutShouldReturnErrorWhenExceptionWasRaised(self, mockApp):
        url = f'{self.USERAPI_BASE_URL}/logout'
        userauth = Config.getAuthService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError
        ]

        for e in exceptionsToTest:
            userauth.logout.side_effect = e('Some error')

            with mockApp.test_client() as client:
                response = client.post(url)

                assert response.status_code == e.getStatusCode()

    def test_sessionShouldReturnResultFromSessionMiddlewareAsData(self, mockApp):
        expectedData = { 'sessionUser': DEFAULT_RETURN_LOGIN }

        def mockAddCurrentUser(response):
            response.set_data( json.dumps(expectedData) )
            return response

        mockRequestUser = Config.getRequestUserManager(mockApp)
        mockRequestUser.addCurrentUserToResponse.side_effect = mockAddCurrentUser

        url = f'{self.USERAPI_BASE_URL}/session'
        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200
            mockRequestUser.addCurrentUserToResponse.assert_called_once()
            assert response.get_json() == expectedData

    def test_sessionShouldNotCallSearchService(self, mockApp):
        search = Config.getSearchService(mockApp)

        url = f'{self.USERAPI_BASE_URL}/session'
        with mockApp.test_client() as client:
            response = client.get(url).get_json()

            assert search.searchUsersByKeyValues.call_count == 0
            assert 'result' not in response

    def test_sessionShouldReturnErrorWhenExceptionWasRaised(self, mockApp):
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        mockRequestUser = Config.getRequestUserManager(mockApp)
        url = f'{self.USERAPI_BASE_URL}/session'

        for e in exceptionsToTest:
            mockRequestUser.addCurrentUserToResponse.side_effect = e('some error')
            with mockApp.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()


class TestCORS:
    URL_TO_TEST = [
        TestUserAPIs.USERAPI_BASE_URL,
    ]
    
    def test_apiConnectionWithOptionMethodShouldReturnCORSHeaders(self, client):
        for url in self.URL_TO_TEST:
            response = client.options(url)

            headers = response.headers
            assert headers.get('Access-Control-Allow-Origin') == '*'
            assert headers.get('Access-Control-Allow-Headers') == '*'
            assert headers.get('Access-Control-Allow-Methods') == '*'

    def test_apiConnectionShouldReturnCORSHeaders(self, client):
        for url in self.URL_TO_TEST:
            response = client.get(url)

            headers = response.headers
            assert headers.get('Access-Control-Allow-Origin') == '*'
