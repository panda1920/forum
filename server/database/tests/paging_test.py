import pdb
import pytest

from server.database.paging import Paging

class TestPagingConstruction():
    DEFAULT_OFFSET_VALUE = 118
    DEFAULT_LIMIT_VALUE = 32

    def test_constructPaging(self):
        querystringObj = {
            'offset': self.DEFAULT_OFFSET_VALUE,
            'limit': self.DEFAULT_LIMIT_VALUE,
        }
        p = Paging(querystringObj)

        assert p.offset == self.DEFAULT_OFFSET_VALUE
        assert p.limit == self.DEFAULT_LIMIT_VALUE

    def test_constructPagingWithUnrelatedAttributes(self):
        querystringObj = {
            'offset': self.DEFAULT_OFFSET_VALUE,
            'limit': self.DEFAULT_LIMIT_VALUE,
            'unrelated': 'unrelated_value'
        }
        p = Paging(querystringObj)

        assert p.offset == self.DEFAULT_OFFSET_VALUE
        assert p.limit == self.DEFAULT_LIMIT_VALUE

    def test_constructPagingWhenAttributeValueIsConvertableString(self):
        querystringObj = {
            'offset': str( self.DEFAULT_OFFSET_VALUE ),
            'limit': str( self.DEFAULT_LIMIT_VALUE ),
        }
        p = Paging(querystringObj)

        assert p.offset == self.DEFAULT_OFFSET_VALUE
        assert p.limit == self.DEFAULT_LIMIT_VALUE

    def test_construtPagingWithDefaultValueWhenAttributeIsMissing(self):
        querystringObjMissingOffset = {
            'limit': self.DEFAULT_LIMIT_VALUE
        }
        p = Paging(querystringObjMissingOffset)
        assert p.offset == Paging.DEFAULT_OFFSET
        assert p.limit == querystringObjMissingOffset['limit']
        
        querystringObjMissingLimit = {
            'offset': self.DEFAULT_OFFSET_VALUE
        }
        p = Paging(querystringObjMissingLimit)
        assert p.offset == querystringObjMissingLimit['offset']
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