# -*- coding: utf-8 -*-
"""
This file houses tests for all routes available for this app
"""
import json

import pytest

import tests.mocks as mocks
from server.config import Config
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES = 'some_value'
DEFAULT_RETURN_CREATENEWPOST = None
DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES = 'some_value'
DEFAULT_RETURN_SIGNUP = None
DEFAULT_RETURN_UPDATEUSER = 'some_value_updateuser'
DEFAULT_RETURN_UPDATEPOST = 'some_value_updatepost'
DEFAULT_RETURN_DELETEUSER = dict(deleteCount=1)
DEFAULT_RETURN_DELETEPOST = dict(deleteCount=1)
DEFAULT_USER_RETURNED = dict(
    userId='1',
    displayName='Bobby',
    userName='Bobby@myforumwebapp.com',
    imageUrl='http://some-random-website/myforumwebapp.com',
)


@pytest.fixture(scope='function')
def mockApp(app):
    # replace with mock
    mockDB = mocks.createMockDB()
    app.config['DATABASE_REPOSITORY'] = mockDB

    mockCreate = mocks.createMockEntityCreationService()
    mockCreate.signup.return_value = DEFAULT_RETURN_SIGNUP
    mockCreate.createNewPost.return_value = DEFAULT_RETURN_CREATENEWPOST
    app.config['CREATION_SERVICE'] = mockCreate
    
    mockSearch = mocks.createMockSearchService()
    mockSearch.searchPostsByKeyValues.return_value = DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES
    mockSearch.searchUsersByKeyValues.return_value = DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES
    app.config['SEARCH_SERVICE'] = mockSearch

    mockUpdate = mocks.createMockUpdateService()
    mockUpdate.updateUserByKeyValues.return_value = DEFAULT_RETURN_UPDATEUSER
    mockUpdate.updatePostByKeyValues.return_value = DEFAULT_RETURN_UPDATEPOST
    app.config['UPDATE_SERVICE'] = mockUpdate

    mockDelete = mocks.createMockDeleteService()
    mockDelete.deleteUserByKeyValues.return_value = DEFAULT_RETURN_DELETEUSER
    mockDelete.deletePostByKeyValues.return_value = DEFAULT_RETURN_DELETEPOST
    app.config['DELETE_SERVICE'] = mockDelete

    mockUserAuth = mocks.createMockUserAuth()
    mockUserAuth.login.return_value = DEFAULT_USER_RETURNED
    app.config['AUTHENTICATION_SERVICE'] = mockUserAuth

    mockSessionUser = mocks.createMockSessionMiddleware()
    mockSessionUser.addCurrentUserToResponse.side_effect = lambda response: response
    app.config['SESSION_MIDDLEWARE'] = mockSessionUser

    yield app


@pytest.fixture(scope='function')
def client(mockApp):
    with mockApp.test_client() as client:
        yield client


class TestPostAPIs:
    POSTSAPI_BASE_URL = '/v1/posts'

    def test_searchPostsAPIPassesQueryStringToSearchService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(keyValues)

    def test_searchPostsAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            assert response.status_code == 200
            jsonResponse = response.get_json()
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES

    def test_searchPostsReturnsErrorWhenExceptionWasRaised(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        keyValues = dict(
            search='1 2 3 4',
        )

        for e in exceptionsToTest:
            with mockApp.test_client() as client:
                mockSearch.searchPostsByKeyValues.side_effect = e()
                response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

                assert response.status_code == e.getStatusCode()

    def test_searchPostsAPIByIdPassesIdToSearchService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            client.get(url)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def searchPostsByIdAPIIgnoresQueryString(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        keyValues = dict(offset=30, limit=100)

        with mockApp.test_client() as client:
            client.get(url, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def test_searchPostsByIdAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200
            jsonResponse = response.get_json()
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES

    def test_searchPostsByIdAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        for e in exceptionsToTest:
            with mockApp.test_client() as client:
                mockSearch.searchPostsByKeyValues.side_effect = e()
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createPostAPIPassesPostedDataToService(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        newPostData = dict(
            userId='0',
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            client.post(url, json=newPostData)

            mockCreate.createNewPost.assert_called_with(newPostData)

    def test_createPostAPIReturns201(self, mockApp):
        Config.getCreationService(mockApp)
        newPostData = dict(
            userId='0',
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            response = client.post(url, json=newPostData)

            assert response.status_code == 201

    def test_createPostAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        newPostData = dict(
            userId='0',
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]

        for e in exceptionsToTest:
            mockCreate.createNewPost.side_effect = e()
            with mockApp.test_client() as client:
                response = client.post(url, json=newPostData)

                assert response.status_code == e.getStatusCode()

    def test_updatePostShouldPassDataToServiceAndReturn200(self, client, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }

        response = client.patch(url, json=updateData)

        assert response.status_code == 200
        mockUpdate.updatePostByKeyValues.assert_called_with(dict(
            **updateData,
            postId=postIdToUpdate
        ))

    def test_updatePostByPostedMimeTypeNotJsonReturnsError(self, client, mockApp):
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = 'content'
        headers = { 'Content-Type': 'text/plain'}

        response = client.patch(url, data=updateData, headers=headers)

        assert response.status_code == 400

    def test_whenUpdatePostRaisesExceptionReturnError(self, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }
        exceptionsToTest = [
            exceptions.EntityValidationError('Some error'),
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]

        for e in exceptionsToTest:
            mockUpdate.updatePostByKeyValues.side_effect = e
            with mockApp.test_client() as client:
                response = client.patch(url, json=updateData)

            assert response.status_code == e.getStatusCode()

    # def test_deletePostReturns200(self, mockApp):
    #     postIdToDelete = '1'
    #     url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
    #     mockDB = Config.getDB(mockApp)

    #     with mockApp.test_client() as client:
    #         response = client.delete(url)

    #         assert response.status_code == 200

    #         assert mockDB.deletePost.call_count == 1
    #         argPassed = mockDB.deletePost.call_args[0][0]
    #         assert argPassed == [postIdToDelete]

    def test_deletePostByIdShouldPassPostIdToService(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        mockDelete = Config.getDeleteService(mockApp)

        with mockApp.test_client() as client:
            client.delete(url)

            mockDelete.deletePostByKeyValues.assert_called_with( dict(postId=postIdToDelete) )

    def test_deletePostByIdShouldReturn200AndResponseFromService(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200
            responseJson = response.get_json()
            responseJson['deleteCount'] == DEFAULT_RETURN_DELETEPOST

    def test_deletePostByIdShouldReturnsErrorWhenExceptionRaised(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]
        mockDelete = Config.getDeleteService(mockApp)

        for e in exceptionsToTest:
            mockDelete.deletePostByKeyValues.side_effect = e
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()


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

    def test_searchUsersReturns200AearchResultFromService(self, mockApp):
        Config.getSearchService(mockApp)
        keyValues = dict(
            search='username'
        )

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=keyValues)
            jsonResponse = response.get_json()

            assert response.status_code == 200
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES
        
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

    def test_searchUserByExplicitIDReturns200AndSearchResultFromService(self, mockApp):
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            response = client.get(url)
            jsonResponse = response.get_json()

            assert response.status_code == 200
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES

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

    def test_createUserPassesFormDataToService(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
            'password': '12345678'
        }
        url = f'{self.USERAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            client.post(url, json=userProperties)

            mockCreate.signup.assert_called_with(userProperties)

    def test_createUserReturns201WhenSuccess(self, mockApp):
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
            'password': '12345678'
        }
        url = f'{self.USERAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            response = client.post(url, json=userProperties)

            assert response.status_code == 201

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

    def test_updateUserShouldPassDataToServiceAndReturn200(self, client, mockApp):
        mockUpdate = Config.getUpdateService(mockApp)
        userProperties = {
            'displayName': 'Jimmy',
        }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'

        response = client.patch(url, json=userProperties)

        assert response.status_code == 200
        mockUpdate.updateUserByKeyValues(dict(
            userId=userIdToUpdate,
            **userProperties
        ))

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
            mockUpdate.updateUserByKeyValues.side_effect = e
            with mockApp.test_client() as client:
                response = client.patch(url, json=userProperties)

            assert response.status_code == e.getStatusCode()

    def test_deleteUserByIdShouldPassUserIdToDeleteService(self, mockApp):
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'
        mockDelete = Config.getDeleteService(mockApp)

        with mockApp.test_client() as client:
            client.delete(url)

            mockDelete.deleteUserByKeyValues.assert_called_with(dict(
                userId=userIdToDelete
            ))

    def test_deleteUserByIdShouldReturn200AndReturnValueFromService(self, mockApp):
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200
            responseJson = response.get_json()
            responseJson['deleteCount'] == DEFAULT_RETURN_DELETEUSER['deleteCount']

    def test_deleteUserReturnsErrorWhenDeleteUserRaisesException(self, mockApp):
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]
        mockDelete = Config.getDeleteService(mockApp)

        for e in exceptionsToTest:
            mockDelete.deleteUserByKeyValues.side_effect = e
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

    def test_loginShouldReturnUserInfoOnSuccess(self, mockApp, client):
        userCredentials = dict(
            userName='Bobby',
            password='password',
        )
        url = f'{self.USERAPI_BASE_URL}/login'

        response = client.post(url, json=userCredentials)

        data = response.get_json()
        assert 'users' in data
        assert data['users'][0] == DEFAULT_USER_RETURNED

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

        response = client.post(url)

        assert response.status_code == 200
        userauth.logout.assert_called_once()

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
        expectedData = { 'sessionUser': DEFAULT_USER_RETURNED }

        def mockAddCurrentUser(response):
            response.set_data( json.dumps(expectedData) )
            return response

        mockSessionUser = Config.getSessionMiddleware(mockApp)
        mockSessionUser.addCurrentUserToResponse.side_effect = mockAddCurrentUser

        url = f'{self.USERAPI_BASE_URL}/session'
        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200
            mockSessionUser.addCurrentUserToResponse.assert_called_once()
            assert response.get_json() == expectedData

    def test_sessionShouldReturnErrorWhenExceptionWasRaised(self, mockApp):
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        mockSessionUser = Config.getSessionMiddleware(mockApp)
        url = f'{self.USERAPI_BASE_URL}/session'

        for e in exceptionsToTest:
            mockSessionUser.addCurrentUserToResponse.side_effect = e('some error')
            with mockApp.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()


class TestCORS:
    URL_TO_TEST = [
        '/v1/users',
        '/v1/posts',
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
