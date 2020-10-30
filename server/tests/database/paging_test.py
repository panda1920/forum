# -*- coding: utf-8 -*-
"""
This file houses tests for paging.py
"""

import pytest

from server.database.paging import Paging, PagingNoLimit

TEST_OFFSET_VALUE = 118
TEST_LIMIT_VALUE = 32


class TestPagingConstruction:
    def test_constructPaging(self):
        querystringObj = {
            'offset': TEST_OFFSET_VALUE,
            'limit': TEST_LIMIT_VALUE,
        }
        p = Paging(querystringObj)

        assert p._offset == TEST_OFFSET_VALUE
        assert p._limit == TEST_LIMIT_VALUE

    def test_constructPagingWithUnrelatedAttributes(self):
        querystringObj = {
            'offset': TEST_OFFSET_VALUE,
            'limit': TEST_LIMIT_VALUE,
            'unrelated': 'unrelated_value'
        }
        p = Paging(querystringObj)

        assert p._offset == TEST_OFFSET_VALUE
        assert p._limit == TEST_LIMIT_VALUE

    def test_constructPagingWhenAttributeValueIsConvertableString(self):
        querystringObj = {
            'offset': str( TEST_OFFSET_VALUE ),
            'limit': str( TEST_LIMIT_VALUE ),
        }
        p = Paging(querystringObj)

        assert p._offset == TEST_OFFSET_VALUE
        assert p._limit == TEST_LIMIT_VALUE

    def test_construtPagingWithDefaultValueWhenAttributeIsMissing(self):
        querystringObjMissingOffset = {
            'limit': TEST_LIMIT_VALUE
        }
        p = Paging(querystringObjMissingOffset)
        assert p._offset == Paging.DEFAULT_OFFSET
        assert p._limit == TEST_LIMIT_VALUE
        
        querystringObjMissingLimit = {
            'offset': TEST_OFFSET_VALUE
        }
        p = Paging(querystringObjMissingLimit)
        
        assert p._offset == TEST_OFFSET_VALUE
        assert p._limit == Paging.DEFAULT_LIMIT

    def test_constructPagingWith0Limit0Offset(self):
        querystringObj = {
            'offset': 0,
            'limit': 0,
        }
        p = Paging(querystringObj)

        assert p._offset == 0
        assert p._limit == 0

    def test_constructPagingWithDefaultValueWhenNegativeAttributeIsPassed(self):
        querystringObjs = [
            {'offset': -100, 'limit': -50},
            {'offset': -1, 'limit': -1},
        ]
        for querystringObj in querystringObjs:
            p = Paging(querystringObj)

            assert p._offset == Paging.DEFAULT_OFFSET
            assert p._limit == Paging.DEFAULT_LIMIT

    def test_constructPagingWithDefaultValueWhenUncovertableValueIsPassed(self):
        querystringObjs = [
            {'offset': 'hello', 'limit': 'world'},
            {'offset': [], 'limit': [1, 2, 3]},
            {'offset': {'name': 'name'}, 'limit': {}},
        ]
        for querystringObj in querystringObjs:
            p = Paging(querystringObj)

            assert p._offset == Paging.DEFAULT_OFFSET
            assert p._limit == Paging.DEFAULT_LIMIT

    def test_constructPagingWithFloorValueWhenRealNumberIsPassed(self):
        querystringObj = {
            'offset': 1.11,
            'limit': 9.99,
        }
        p = Paging(querystringObj)

        assert p._offset == 1
        assert p._limit == 9


class TestPagingNoLimitConstruction:
    def test_constructPagingWithDefaultOffsetAndNoLimitWhenNoConstructorArgs(self):
        p = PagingNoLimit()
        
        assert p._offset == Paging.DEFAULT_OFFSET
        assert p._limit is None

    def test_constructionWithNoLimitWhenPassedQuerystring(self):
        querystringObj = {
            'offset': TEST_OFFSET_VALUE,
            'limit': TEST_LIMIT_VALUE,
        }
        p = PagingNoLimit(querystringObj)

        assert p._offset == TEST_OFFSET_VALUE
        assert p._limit is None


class TestPagingMethods:
    DEFAULT_LIMIT = 3
    DEFAULT_OFFSET = 2

    @pytest.fixture(scope='function')
    def paging(self):
        return Paging(dict(
            offset=self.DEFAULT_OFFSET,
            limit=self.DEFAULT_LIMIT,
        ))

    @pytest.fixture(scope='function')
    def nolimit(self):
        return PagingNoLimit(dict(
            offset=self.DEFAULT_OFFSET
        ))
    
    def test_pagingSlice(self):
        somelist = [1, 2, 3, 4, 5]
        pagingParams = [
            dict(offset=0, limit=3),
            dict(offset=0, limit=5),
            dict(offset=0, limit=6),
            dict(offset=2, limit=3),
            dict(offset=4, limit=3),
            dict(offset=0, limit=0),
        ]
        expectedSlices = [
            [1, 2, 3],
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            [3, 4, 5],
            [5],
            []
        ]

        for param, expected in zip(pagingParams, expectedSlices):
            paging = Paging(param)

            assert expected == paging.slice(somelist)

    def test_pagingNoLimitSlice(self):
        somelist = [1, 2, 3, 4, 5]
        pagingParams = [
            dict(offset=0, limit=3),
            dict(offset=0, limit=5),
            dict(offset=0, limit=6),
            dict(offset=2, limit=3),
            dict(offset=4, limit=3),
            dict(offset=0, limit=0),
        ]
        expectedSlices = [
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            [3, 4, 5],
            [5],
            [1, 2, 3, 4, 5],
        ]

        for param, expected in zip(pagingParams, expectedSlices):
            paging = PagingNoLimit(param)

            assert expected == paging.slice(somelist)
