# -*- coding: utf-8 -*-
"""
This file houses tests for CORS
"""
import pytest

import os

from server.config import Config


@pytest.fixture(scope='function', autouse=True)
def set_mock_returnvalues(mockApp):
    search = Config.getSearchService(mockApp)

    search.searchUsersByKeyValues.return_value = dict(users=[])
    search.searchPostsByKeyValues.return_value = dict(posts=[])
    search.searchThreadsByKeyValues.return_value = dict(threads=[])
    search.searchBoardsByKeyValues.return_value = dict(boards=[])

    yield

    search.searchUsersByKeyValues.reset_mock()
    search.searchPostsByKeyValues.reset_mock()
    search.searchThreadsByKeyValues.reset_mock()
    search.searchBoardsByKeyValues.reset_mock()


@pytest.fixture(scope='module', autouse=True)
def set_testflag_off(mockApp):
    mockApp.testing = False

    yield

    mockApp.testing = True


URL_TO_TEST = [
    '/v1/users',
    '/v1/posts',
    '/v1/threads',
    '/v1/boards',
]

# custom header to prevent CSRF attacks
CUSTOM_HEADER = {
    'X-Requested-With': 'some_value',
}


class TestCORS:
    def test_CORSPreflightShouldReturnCORSHeaders(self, client):
        expected_origins = os.getenv('CORS_ALLOWED_ORIGINS')
        expected_headers = os.getenv('CORS_ALLOWED_HEADERS')
        expected_methods = os.getenv('CORS_ALLOWED_METHODS')
        
        for url in URL_TO_TEST:
            response = client.options(url)

            assert response.status_code == 204  # should have no content

            headers = response.headers
            assert headers.get('Access-Control-Allow-Origin') == expected_origins
            assert headers.get('Access-Control-Allow-Headers') == expected_headers
            assert headers.get('Access-Control-Allow-Methods') == expected_methods

    def test_CORSRequestNoCustomHeaderShouldReturnBadRequest(self, client):
        expected_origins = os.getenv('CORS_ALLOWED_ORIGINS')
        request_headers = { 'Origin': os.getenv('CORS_ALLOWED_ORIGINS').split(', ')[0] }
        
        for url in URL_TO_TEST:
            response = client.get(url, headers=request_headers)

            assert response.status_code == 400

            headers = response.headers
            assert headers.get('Access-Control-Allow-Origin') == expected_origins

    def test_CORSRequestWithCustomHeadersShouldBeSuccesful(self, client):
        expected_origins = os.getenv('CORS_ALLOWED_ORIGINS')
        request_headers = { 'Origin': os.getenv('CORS_ALLOWED_ORIGINS').split(', ')[0] }
        request_headers.update(CUSTOM_HEADER)
        
        for url in URL_TO_TEST:
            response = client.get(url, headers=request_headers)

            assert response.status_code == 200

            headers = response.headers
            assert headers.get('Access-Control-Allow-Origin') == expected_origins


class TestCSRF:
    def test_RequestWithCustomHeaderShouldProcessRequest(self, client, mockApp):
        search = Config.getSearchService(mockApp)
        
        for url in URL_TO_TEST:
            client.get(url, headers=CUSTOM_HEADER)

        assert search.searchUsersByKeyValues.call_count == 1
        assert search.searchPostsByKeyValues.call_count == 1
        assert search.searchThreadsByKeyValues.call_count == 1
        assert search.searchBoardsByKeyValues.call_count == 1

    def test_RequestWithNoCustomHeaderShouldNotProcessRequest(self, client, mockApp):
        search = Config.getSearchService(mockApp)
        
        for url in URL_TO_TEST:
            client.get(url)

            assert search.searchUsersByKeyValues.call_count == 0
            assert search.searchPostsByKeyValues.call_count == 0
            assert search.searchThreadsByKeyValues.call_count == 0
            assert search.searchBoardsByKeyValues.call_count == 0
