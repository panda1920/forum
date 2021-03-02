# -*- coding: utf-8 -*-
"""
This file houses tests for User related routes available for this app
"""
import json
import pytest
from pathlib import Path

from server.config import Config
from server.entity import User
from tests.helpers import create_mock_entities, create_testuser_attrs
import server.exceptions as exceptions


DEFAULT_RETURN_SEARCHUSER_ATTRSET = [
    create_testuser_attrs(userId='test_userid1'),
    create_testuser_attrs(userId='test_userid2'),
    create_testuser_attrs(userId='test_userid3'),
]
DEFAULT_RETURN_SEARCHUSER = create_mock_entities(DEFAULT_RETURN_SEARCHUSER_ATTRSET)
DEFAULT_RETURN_SIGNUP = dict(created='user')
DEFAULT_RETURN_UPDATEUSER = 'some_value_updateuser'
DEFAULT_RETURN_DELETEUSER = dict(deleteCount=1)
DEFAULT_RETURN_LOGIN = dict()
DEFAULT_RETURN_LOGOUT = dict()
DEFAULT_UPLOAD_FILE = Path(__file__).resolve().parents[1] / 'testdata' / 'sample_image.png'


@pytest.fixture(scope='function', autouse=True)
def set_mock_returnvalues(mockApp):
    Config.getCreationService(mockApp) \
        .signup.return_value = DEFAULT_RETURN_SIGNUP
    
    Config.getSearchService(mockApp) \
        .searchUsersByKeyValues.return_value = dict(users=DEFAULT_RETURN_SEARCHUSER)

    Config.getUpdateService(mockApp) \
        .updateUser.return_value = DEFAULT_RETURN_UPDATEUSER

    Config.getDeleteService(mockApp) \
        .deleteUserById.return_value = DEFAULT_RETURN_DELETEUSER

    Config.getAuthService(mockApp) \
        .login.return_value = DEFAULT_RETURN_LOGIN
    
    Config.getAuthService(mockApp) \
        .logout.return_value = DEFAULT_RETURN_LOGOUT

    Config.getRequestUserManager(mockApp) \
        .addCurrentUserToResponse.side_effect = lambda response: response


@pytest.fixture(scope='function', autouse=True)
def reset_mocks(mockApp):
    yield

    for mock in DEFAULT_RETURN_SEARCHUSER:
        mock.reset_mock(side_effect=True)

    Config.getCreationService(mockApp) \
        .signup.reset_mock(side_effect=True)
    
    Config.getSearchService(mockApp) \
        .searchUsersByKeyValues.reset_mock(side_effect=True)

    Config.getUpdateService(mockApp) \
        .updateUser.reset_mock(side_effect=True)

    Config.getDeleteService(mockApp) \
        .deleteUserById.reset_mock(side_effect=True)

    Config.getAuthService(mockApp) \
        .login.reset_mock(side_effect=True)
    
    Config.getAuthService(mockApp) \
        .logout.reset_mock(side_effect=True)

    Config.getAuthService(mockApp) \
        .confirm_user_credential.reset_mock(side_effect=True)

    Config.getRequestUserManager(mockApp) \
        .addCurrentUserToResponse.reset_mock(side_effect=True)


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

    def test_updateUserPortraitShouldPassUserEntityToServiceAndReturn200(self, client, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)

        with DEFAULT_UPLOAD_FILE.open('rb') as upload_file:
            filedata = upload_file.read()
            upload_file.seek(0)  # reset file pointer position
            userIdToUpdate = '1'
            params = { 'portraitImage': upload_file }
            url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update-portrait'

            response = client.patch(url, data=params)

            assert response.status_code == 200
            passed_user, *_ = mockUpdate.updateUser.call_args_list[0][0]
            assert isinstance(passed_user, User)
            assert passed_user.userId == userIdToUpdate
            assert passed_user.portraitImage == filedata

    def test_updateUserShouldReturnErrorWhenNoFileWasFound(self, client):
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update-portrait'

        response = client.patch(url)

        response.status_code == exceptions.InvalidRequest.getStatusCode()

    def test_updateUserPortraitReturnsErrorWhenUpdateUserRaisesException(self, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update-portrait'
        exceptionsToTest = [
            exceptions.EntityValidationError('some error'),
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
            exceptions.UnauthorizedError('some error'),
            exceptions.InvalidImageFileError('some error'),
        ]

        for e in exceptionsToTest:
            with DEFAULT_UPLOAD_FILE.open('rb') as upload_file, mockApp.test_client() as client:
                    
                mockUpdate.updateUser.side_effect = e
                params = { 'portraitImage': upload_file }

                response = client.patch(url, data=params)

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

    def test_confirmShouldPassCredentialsToAuthService(self, mockApp, client):
        user_id = 'test_id'
        url = f'{self.USERAPI_BASE_URL}/{user_id}/confirm'
        data = { 'password': 'some_password' }
        user_auth = Config.getAuthService(mockApp)

        client.post(url, json=data)

        user_auth.confirm_user_credential.assert_called_once
        user_auth.confirm_user_credential.assert_called_with(
            user_id, data['password']
        )

    def test_confirmShouldReturn200WhenAuthSuccessful(self, mockApp, client):
        user_id = 'test_id'
        url = f'{self.USERAPI_BASE_URL}/{user_id}/confirm'
        data = { 'password': 'some_password' }
        user_auth = Config.getAuthService(mockApp)
        user_auth.confirm_user_credential.return_value = True

        response = client.post(url, json=data)

        assert response.status_code == 200

    def test_confirmShouldReturnErrorWhenExceptionRaised(self, mockApp):
        user_id = 'test_id'
        url = f'{self.USERAPI_BASE_URL}/{user_id}/confirm'
        data = { 'password': 'some_password' }
        user_auth = Config.getAuthService(mockApp)
        exceptions_raised = [
            exceptions.InvalidUserCredentials,
            exceptions.ServerMiscError,
            exceptions.UnauthorizedError,
        ]

        for e in exceptions_raised:
            user_auth.confirm_user_credential.side_effect = e()

            with mockApp.test_client() as client:
                response = client.post(url, json=data)

                assert response.status_code == e.getStatusCode()
