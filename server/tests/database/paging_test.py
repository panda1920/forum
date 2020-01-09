import pdb
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

        assert p.offset == TEST_OFFSET_VALUE
        assert p.limit == TEST_LIMIT_VALUE

    def test_constructPagingWithUnrelatedAttributes(self):
        querystringObj = {
            'offset': TEST_OFFSET_VALUE,
            'limit': TEST_LIMIT_VALUE,
            'unrelated': 'unrelated_value'
        }
        p = Paging(querystringObj)

        assert p.offset == TEST_OFFSET_VALUE
        assert p.limit == TEST_LIMIT_VALUE

    def test_constructPagingWhenAttributeValueIsConvertableString(self):
        querystringObj = {
            'offset': str( TEST_OFFSET_VALUE ),
            'limit': str( TEST_LIMIT_VALUE ),
        }
        p = Paging(querystringObj)

        assert p.offset == TEST_OFFSET_VALUE
        assert p.limit == TEST_LIMIT_VALUE

    def test_construtPagingWithDefaultValueWhenAttributeIsMissing(self):
        querystringObjMissingOffset = {
            'limit': TEST_LIMIT_VALUE
        }
        p = Paging(querystringObjMissingOffset)
        assert p.offset == Paging.DEFAULT_OFFSET
        assert p.limit == TEST_LIMIT_VALUE
        
        querystringObjMissingLimit = {
            'offset': TEST_OFFSET_VALUE
        }
        p = Paging(querystringObjMissingLimit)
        
        assert p.offset == TEST_OFFSET_VALUE
        assert p.limit == Paging.DEFAULT_LIMIT

    def test_constructPagingWith0Limit0Offset(self):
        querystringObj = {
            'offset': 0,
            'limit': 0,
        }
        p = Paging(querystringObj)

        assert p.offset == 0
        assert p.limit == 0

    def test_constructPagingWithDefaultValueWhenNegativeAttributeIsPassed(self):
        querystringObjs = [
            {'offset': -100, 'limit': -50},
            {'offset': -1, 'limit': -1},
        ]
        for querystringObj in querystringObjs:
            p = Paging(querystringObj)

            assert p.offset == Paging.DEFAULT_OFFSET
            assert p.limit == Paging.DEFAULT_LIMIT

    def test_constructPagingWithDefaultValueWhenUncovertableValueIsPassed(self):
        querystringObjs = [
            {'offset': 'hello', 'limit': 'world'},
            {'offset': [], 'limit': [1, 2, 3]},
            {'offset': {'name': 'name'}, 'limit': {}},
        ]
        for querystringObj in querystringObjs:
            p = Paging(querystringObj)

            assert p.offset == Paging.DEFAULT_OFFSET
            assert p.limit == Paging.DEFAULT_LIMIT

    def test_constructPagingWithFloorValueWhenRealNumberIsPassed(self):
        querystringObj = {
            'offset': 1.11,
            'limit': 9.99,
        }
        p = Paging(querystringObj)

        assert p.offset == 1
        assert p.limit == 9

class TestPagingNoLimitConstruction:
    def test_constructPagingWithDefaultOffsetAndNoLimitWhenNoConstructorArgs(self):
        p = PagingNoLimit()
        
        assert p.offset == Paging.DEFAULT_OFFSET
        assert p.limit == None

    def test_constructionWithNoLimitWhenPassedQuerystring(self):
        querystringObj = {
            'offset': TEST_OFFSET_VALUE,
            'limit': TEST_LIMIT_VALUE,
        }
        p = PagingNoLimit(querystringObj)

        assert p.offset == TEST_OFFSET_VALUE
        assert p.limit == None