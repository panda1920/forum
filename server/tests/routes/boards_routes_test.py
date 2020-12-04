# -*- coding: utf-8 -*-
"""
This file houses tests for Board related routes available for this app
"""

import pytest

from server.config import Config
from server.entity import Board
from tests.helpers import create_mock_entities, create_testboard_attrs
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHBOARD_ATTRSET = [
    create_testboard_attrs(boardId='test_boardid1'),
    create_testboard_attrs(boardId='test_boardid2'),
    create_testboard_attrs(boardId='test_boardid3'),
]
DEFAULT_RETURN_SEARCHBOARD = create_mock_entities(DEFAULT_RETURN_SEARCHBOARD_ATTRSET)
DEFAULT_RETURN_CREATENEWBOARD = dict(created='board')
DEFAULT_RETURN_UPDATEBOARD = 'some_value_updateboard'
DEFAULT_RETURN_DELETEBOARD = dict(deleteCount=1)


@pytest.fixture(scope='function', autouse=True)
def set_mock_returnvalues(mockApp):
    Config.getSearchService(mockApp) \
        .searchBoardsByKeyValues.return_value = dict(boards=DEFAULT_RETURN_SEARCHBOARD)


@pytest.fixture(scope='function', autouse=True)
def reset_mocks():
    yield

    for mock in DEFAULT_RETURN_SEARCHBOARD:
        mock.reset_mock(side_effect=True)


class TestBoardAPIs:
    BOARDSAPI_BASE_URL = '/v1/boards'

    def test_searchBoardsAPIShouldPassQueryStringToSearchService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            client.get(self.BOARDSAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchBoardsByKeyValues.assert_called_with(keyValues)

    def test_searchBoardsAPIShouldReturnSerializedBoardData(self, mockApp):
        keyValues = dict(
            search='1 2 3 4',
        )
        print()

        with mockApp.test_client() as client:
            response = client.get(self.BOARDSAPI_BASE_URL, query_string=keyValues)

            assert response.status_code == 200
            boards = response.get_json()['result']['boards']
            for idx, board in enumerate(boards):
                assert board == DEFAULT_RETURN_SEARCHBOARD_ATTRSET[idx]

    def test_searchBoardsReturnsErrorWhenExceptionWasRaised(self, mockApp):
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
                mockSearch.searchBoardsByKeyValues.side_effect = e()
                response = client.get(self.BOARDSAPI_BASE_URL, query_string=keyValues)

                assert response.status_code == e.getStatusCode()
