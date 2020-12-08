# -*- coding: utf-8 -*-
"""
This file houses tests for Post related routes available for this app
"""
import pytest

from server.config import Config
from server.entity import Thread
from tests.helpers import create_mock_entities
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHTHREAD_ATTRSET = [
    dict(threadId='test_thread_1', userId='owner1', title='title_1'),
    dict(threadId='test_thread_2', userId='owner1', title='title_2'),
    dict(threadId='test_thread_3', userId='owner1', title='title_3'),
]
DEFAULT_RETURN_CREATENEWTHREAD = dict(created='thread')
DEFAULT_RETURN_UPDATETHREAD = 'some_value_updatethread'
DEFAULT_RETURN_DELETETHREAD = dict(deleteCount=1)
DEFAULT_RETURN_VIEWTHREAD = dict(updatedCount=1)


@pytest.fixture(scope='function', autouse=True)
def set_mock_returnvalues(mockApp):
    Config.getCreationService(mockApp).createNewThread.return_value = DEFAULT_RETURN_CREATENEWTHREAD
    
    mock_returned_threads = create_mock_entities(DEFAULT_RETURN_SEARCHTHREAD_ATTRSET)
    for thread, attrs in zip(mock_returned_threads, DEFAULT_RETURN_SEARCHTHREAD_ATTRSET):
        thread.to_serialize.return_value = attrs
    Config.getSearchService(mockApp).searchThreadsByKeyValues.return_value = dict(threads=mock_returned_threads)

    Config.getUpdateService(mockApp).updateThread.return_value = DEFAULT_RETURN_UPDATETHREAD
    Config.getUpdateService(mockApp).viewThread.return_value = DEFAULT_RETURN_VIEWTHREAD

    Config.getDeleteService(mockApp).deleteThreadById.return_value = DEFAULT_RETURN_DELETETHREAD


@pytest.fixture(scope='function')
def client(mockApp):
    with mockApp.test_client() as client:
        yield client


class TestThreadAPIs:
    THREAD_API_BASE = '/v1/threads'

    def test_searchThreadShouldPassPostedDataToService(self, mockApp, client):
        url = f'{self.THREAD_API_BASE}'
        search_service = Config.getSearchService(mockApp)
        data = dict(search='some title')

        client.get(url, query_string=data)

        search_service.searchThreadsByKeyValues.assert_called_with(data)

    def test_searchThreadShouldCall_to_serializeOnReturnedThreads(self, mockApp, client):
        search_service = Config.getSearchService(mockApp)
        threads = search_service.searchThreadsByKeyValues.return_value['threads']
        url = f'{self.THREAD_API_BASE}'
        data = dict(search='some title')

        client.get(url, query_string=data)

        for thread in threads:
            assert thread.to_serialize.call_count == 1

    def test_searchThreadShouldReturn200AndResultFromService(self, client):
        url = f'{self.THREAD_API_BASE}'
        data = dict(search='some title')
        
        response = client.get(url, query_string=data)

        assert response.status_code == 200
        threads_returned = response.get_json()['result']['threads']
        for thread in threads_returned:
            assert thread in DEFAULT_RETURN_SEARCHTHREAD_ATTRSET

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

    def test_viewThreadShouldPassPostedIdToService(self, mockApp, client):
        update_service = Config.getUpdateService(mockApp)
        threadId = '1'
        url = f'{self.THREAD_API_BASE }/{threadId}/view'

        client.patch(url)

        update_service.viewThread.assert_called_with(threadId)

    def test_viewThreadShouldReturn200AndOperationResult(self, mockApp, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE }/{threadId}/view'

        response = client.patch(url)

        assert response.status_code == 200
        assert response.get_json()['result'] == DEFAULT_RETURN_VIEWTHREAD

    def test_viewThreadShouldReturnErrorWhenServiceRaiseException(self, mockApp):
        threadId = '1'
        url = f'{self.THREAD_API_BASE }/{threadId}/view'
        update_service = Config.getUpdateService(mockApp)
        exceptionsToTest = [
            exceptions.ServerMiscError,
            exceptions.EntityValidationError,
            exceptions.UnauthorizedError
        ]
        
        for e in exceptionsToTest:
            update_service.viewThread.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.patch(url)

                assert response.status_code == e.getStatusCode()

    def test_createThreadShouldPassThreadEntityToService(self, mockApp, client):
        url = f'{self.THREAD_API_BASE}/create'
        creation_service = Config.getCreationService(mockApp)
        data = dict(title='test_title', subject='hello world')

        client.post(url, json=data)

        passed_thread, *_ = creation_service.createNewThread.call_args_list[0][0]
        assert isinstance(passed_thread, Thread)
        for k, v in data.items():
            assert getattr(passed_thread, k) == v

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

    def test_updateThreadByExplicitIdShouldThreadEntityToService(self, mockApp, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/update'
        update_service = Config.getUpdateService(mockApp)
        data = dict(title='test_title', subject='hello world')

        client.patch(url, json=data)

        passed_thread, *_ = update_service.updateThread.call_args_list[0][0]
        assert isinstance(passed_thread, Thread)
        for k, v in data.items():
            assert getattr(passed_thread, k) == v
        assert getattr(passed_thread, 'threadId') == threadId

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
            update_service.updateThread.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.patch(url, json=data)

                assert response.status_code == e.getStatusCode()

    def test_deleteThreadByExplicitIdShouldPassIdToService(self, mockApp, client):
        threadId = '1'
        url = f'{self.THREAD_API_BASE}/{threadId}/delete'
        delete_service = Config.getDeleteService(mockApp)

        client.delete(url)

        delete_service.deleteThreadById.assert_called_with(threadId)

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
            delete_service.deleteThreadById.side_effect = e('some-error')
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()


class TestCORS:
    URL_TO_TEST = [
        TestThreadAPIs.THREAD_API_BASE,
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
