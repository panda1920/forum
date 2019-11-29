import pdb
import pytest

from server.database.paging import Paging

class TestPagingConstruction():
    TEST_OFFSET_VALUE = 118
    TEST_LIMIT_VALUE = 32

    def test_constructPaging(self):
        querystringObj = {
            'offset': self.TEST_OFFSET_VALUE,
            'limit': self.TEST_LIMIT_VALUE,
        }
        p = Paging(querystringObj)

        assert p.offset == self.TEST_OFFSET_VALUE
        assert p.limit == self.TEST_LIMIT_VALUE

    def test_constructPagingWithUnrelatedAttributes(self):
        querystringObj = {
            'offset': self.TEST_OFFSET_VALUE,
            'limit': self.TEST_LIMIT_VALUE,
            'unrelated': 'unrelated_value'
        }
        p = Paging(querystringObj)

        assert p.offset == self.TEST_OFFSET_VALUE
        assert p.limit == self.TEST_LIMIT_VALUE

    def test_constructPagingWhenAttributeValueIsConvertableString(self):
        querystringObj = {
            'offset': str( self.TEST_OFFSET_VALUE ),
            'limit': str( self.TEST_LIMIT_VALUE ),
        }
        p = Paging(querystringObj)

        assert p.offset == self.TEST_OFFSET_VALUE
        assert p.limit == self.TEST_LIMIT_VALUE

    def test_construtPagingWithDefaultValueWhenAttributeIsMissing(self):
        querystringObjMissingOffset = {
            'limit': self.TEST_LIMIT_VALUE
        }
        p = Paging(querystringObjMissingOffset)
        assert p.offset == Paging.DEFAULT_OFFSET
        assert p.limit == self.TEST_LIMIT_VALUE
        
        querystringObjMissingLimit = {
            'offset': self.TEST_OFFSET_VALUE
        }
        p = Paging(querystringObjMissingLimit)
        
        assert p.offset == self.TEST_OFFSET_VALUE
        assert p.limit == Paging.DEFAULT_LIMIT

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