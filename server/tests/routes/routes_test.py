# -*- coding: utf-8 -*-
"""
This file houses tests for all routes available for this app
"""
import json

import pytest

import tests.mocks as mocks
from server.config import Config
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES = 'some_users'
DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES = 'some_posts'
DEFAULT_RETURN_SEARCHTHREADSBYKEYVALUES = 'some_threads'
DEFAULT_RETURN_SEARCHTHREADSBYEXPLICITID = 'some_threads_id'
DEFAULT_RETURN_SIGNUP = dict(created='user')
DEFAULT_RETURN_CREATENEWPOST = dict(created='post')
DEFAULT_RETURN_CREATENEWTHREAD = dict(created='thread')
DEFAULT_RETURN_UPDATEUSER = 'some_value_updateuser'
DEFAULT_RETURN_UPDATEPOST = 'some_value_updatepost'
DEFAULT_RETURN_UPDATETHREAD = 'some_value_updatethread'
DEFAULT_RETURN_DELETEUSER = dict(deleteCount=1)
DEFAULT_RETURN_DELETEPOST = dict(deleteCount=1)
DEFAULT_RETURN_DELETETHREAD = dict(deleteCount=1)
DEFAULT_RETURN_LOGOUT = dict(logout=True)
DEFAULT_USER_RETURNED = dict(
    userId='1',
    displayName='Bobby',
    userName='Bobby@myforumwebapp.com',
    imageUrl='http://some-random-website/myforumwebapp.com',
)


@pytest.fixture(scope='function')
def mockApp(app):
    # replace with mock
    mockDB = mocks.createMockRepo()
    app.config['DATABASE_REPOSITORY'] = mockDB

    mockCreate = mocks.createMockEntityCreationService()
    mockCreate.signup.return_value = DEFAULT_RETURN_SIGNUP
    mockCreate.createNewPost.return_value = DEFAULT_RETURN_CREATENEWPOST
    mockCreate.createNewThread.return_value = DEFAULT_RETURN_CREATENEWTHREAD
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
    mockUserAuth.logout.return_value = DEFAULT_RETURN_LOGOUT
    app.config['AUTHENTICATION_SERVICE'] = mockUserAuth

    mockSessionUser = mocks.createMockRequestUserManager()
    mockSessionUser.addCurrentUserToResponse.side_effect = lambda response: response
    app.config['REQUESTUSER_MIDDLEWARE'] = mockSessionUser

    yield app


@pytest.fixture(scope='function')
def client(mockApp):
    with mockApp.test_client() as client:
        yield client


class TestThreadAPIs:
    THREAD_API_BASE = '/v1/threads'

    @pytest.fixture(scope='function', autouse=True)
    def setup_mock(self, mockApp):
        search = Config.getSearchService(mockApp)
        search.searchThreadsByKeyValues.return_value = DEFAULT_RETURN_SEARCHTHREADSBYKEYVALUES
        search.searchThreadByExplicitId.return_value = DEFAULT_RETURN_SEARCHTHREADSBYEXPLICITID
        create = Config.getCreationService(mockApp)
        create.createNewThread.return_value = DEFAULT_RETURN_CREATENEWTHREAD
        update = Config.getUpdateService(mockApp)
        update.updateThreadByKeyValues.return_value = DEFAULT_RETURN_UPDATETHREAD
        delete = Config.getDeleteService(mockApp)
        delete.deleteThreadByKeyValues.return_value = DEFAULT_RETURN_DELETETHREAD

    def test_searchThreadShouldPassPostedDataToService(self, mockApp, client):
        url = f'{self.THREAD_API_BASE}'
        search_service = Config.getSearchService(mockApp)
        data = dict(search='some title')

        client.get(url, query_string=data)

        search_service.searchThreadsByKeyValues.assert_called_with(data)

    def test_searchThreadShouldReturn200AndResultFromService(self, client):
        url = f'{self.THREAD_API_BASE}'
        data = dict(search='some title')
        
        response = client.get(url, query_string=data)

        assert response.status_code == 200
        assert response.get_json()['result'] == DEFAULT_RETURN_SEARCHTHREADSBYKEYVALUES

    def test_searchThreadShouldReturnErrorWhenServiceRaiseException(self, mockApp):
        url = f'{self.THREAD_API_BASE}'
        search_service = Config.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError,
            exceptions.EntityValidationError,
            exceptions.UnauthorizedError
        ]
        data = dict(search='some title')
        
        for e in exceptionsToTest:
            search_service.searchThreadsByKeyValues.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.get(url, query_string=data)

                assert response.status_code == e.getStatusCode()

    def test_searchThreadByExplicitIdShouldPassPostedDataAndIdToService(self, mockApp, client):
        search_service = Config.getSearchService(mockApp)
        threadId = '1'
        url = f'{self.THREAD_API_BASE }/{threadId}'

        client.get(url)

        search_service.searchThreadByExplicitId.assert_called_with(threadId)

    def test_searchThreadByExplicitIdShouldReturn200AndResultFromService(self, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE }/{threadId}'
        
        response = client.get(url)

        assert response.status_code == 200
        assert response.get_json()['result'] == DEFAULT_RETURN_SEARCHTHREADSBYEXPLICITID

    def test_searchThreadByExplicitIdShouldReturnErrorWhenServiceRaiseException(self, mockApp):
        threadId = '1'
        url = f'{self.THREAD_API_BASE }/{threadId}'
        search_service = Config.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError,
            exceptions.EntityValidationError,
            exceptions.UnauthorizedError
        ]
        
        for e in exceptionsToTest:
            search_service.searchThreadByExplicitId.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createThreadShouldPassPostedDataToService(self, mockApp, client):
        url = f'{self.THREAD_API_BASE}/create'
        creation_service = Config.getCreationService(mockApp)
        data = dict(title='test_title', subject='hello world')

        client.post(url, json=data)

        creation_service.createNewThread.assert_called_with(data)

    def test_createThreadShouldReturn201AndResultFromService(self, client):
        url = f'{self.THREAD_API_BASE}/create'
        data = dict(title='test_title', subject='hello world')
        
        response = client.post(url, json=data)

        assert response.status_code == 201
        assert response.get_json()['result'] == DEFAULT_RETURN_CREATENEWTHREAD

    def test_createThreadShouldReturnErrorWhenServiceRaiseException(self, mockApp):
        url = f'{self.THREAD_API_BASE}/create'
        creation_service = Config.getCreationService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError,
            exceptions.EntityValidationError,
            exceptions.UnauthorizedError
        ]
        data = dict(title='test_title', subject='hello world')
        
        for e in exceptionsToTest:
            creation_service.createNewThread.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.post(url, json=data)

                assert response.status_code == e.getStatusCode()

    def test_updateThreadByExplicitIdShouldPassPostedDataAndIdToService(self, mockApp, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/update'
        update_service = Config.getUpdateService(mockApp)
        data = dict(title='test_title', subject='hello world')

        client.patch(url, json=data)

        expectedArg = data.copy()
        expectedArg.update( dict(threadId=threadId) )
        update_service.updateThreadByKeyValues.assert_called_with(expectedArg)

    def test_updateThreadByExplicitIdShouldReturn200AndResultFromService(self, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/update'
        data = dict(title='test_title', subject='hello world')
        
        response = client.patch(url, json=data)

        assert response.status_code == 200
        assert response.get_json()['result'] == DEFAULT_RETURN_UPDATETHREAD

    def test_updateThreadByExplicitIdShouldReturnErrorWhenServiceRaiseException(self, mockApp):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/update'
        update_service = Config.getUpdateService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError,
            exceptions.EntityValidationError,
            exceptions.UnauthorizedError
        ]
        data = dict(title='test_title', subject='hello world')
        
        for e in exceptionsToTest:
            update_service.updateThreadByKeyValues.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.patch(url, json=data)

                assert response.status_code == e.getStatusCode()

    def test_deleteThreadByExplicitIdShouldIdToService(self, mockApp, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/delete'
        delete_service = Config.getDeleteService(mockApp)

        client.delete(url)

        expectedArg = dict(threadId=threadId)
        delete_service.deleteThreadByKeyValues.assert_called_with(expectedArg)

    def test_deleteThreadByExplicitIdShouldReturn202AndResultFromService(self, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/delete'
        
        response = client.delete(url)

        assert response.status_code == 202
        assert response.get_json()['result'] == DEFAULT_RETURN_DELETETHREAD

    def test_deleteThreadByExplicitIdShouldReturnErrorWhenServiceRaiseException(self, mockApp):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/delete'
        delete_service = Config.getDeleteService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError,
            exceptions.EntityValidationError,
            exceptions.UnauthorizedError
        ]
        
        for e in exceptionsToTest:
            delete_service.deleteThreadByKeyValues.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.delete(url)

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
