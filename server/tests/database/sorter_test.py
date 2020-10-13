# -*- coding: utf-8 -*-
"""
This file houses tests for sorter.py
"""
from unittest.mock import MagicMock

import pytest

from server.exceptions import FieldNotFoundInEntityError
from server.database.sorter import AscendingSorter, DescendingSorter, NullSorter
from tests.mocks import createMockEntity


def create_testdata():
    testdata = {}
    entitydata = [
        dict(username='bobby', age=23, ),
        dict(username='zack', age=24, ),
        dict(username='charlie', age=30, ),
        dict(username='anderson', age=25, ),
    ]

    testdata['ENTITIES'] = [
        create_entity_from_dict(d) for d in entitydata
    ]
    testdata['ASC_SORTED_BY_USERNAME'] = [
        testdata['ENTITIES'][3],
        testdata['ENTITIES'][0],
        testdata['ENTITIES'][2],
        testdata['ENTITIES'][1],
    ]
    testdata['ASC_SORTED_BY_AGE'] = [
        testdata['ENTITIES'][0],
        testdata['ENTITIES'][1],
        testdata['ENTITIES'][3],
        testdata['ENTITIES'][2],
    ]
    testdata['DESC_SORTED_BY_USERNAME'] = testdata['ASC_SORTED_BY_USERNAME'].copy()
    testdata['DESC_SORTED_BY_USERNAME'].reverse()
    testdata['DESC_SORTED_BY_AGE'] = testdata['ASC_SORTED_BY_AGE'].copy()
    testdata['DESC_SORTED_BY_AGE'].reverse()

    return testdata


def create_entity_from_dict(d):
    entity = createMockEntity()
    for k, v in d.items():
        setattr(entity, k, v)

    return entity


TEST_DATA = create_testdata()


class TestAscendingSorter:
    def test_sortEntityShouldSortEntityBySpecifiedStringFieldInAscendingOrder(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = AscendingSorter('username')
        
        sorted_entity = sorter.sort(entities)

        assert sorted_entity == TEST_DATA['ASC_SORTED_BY_USERNAME']
        for s, t in zip(sorted_entity, TEST_DATA['ASC_SORTED_BY_USERNAME']):
            assert s.username == t.username

    def test_sortEntityShouldSortEntityBySpecifiedNumberFieldInAscendingOrder(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = AscendingSorter('age')
        
        sorted_entity = sorter.sort(entities)

        assert sorted_entity == TEST_DATA['ASC_SORTED_BY_AGE']

    def test_sortEntityShouldRaiseExceptionWhenKeyNotExist(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = AscendingSorter('non_exist')
        
        with pytest.raises(FieldNotFoundInEntityError):
            sorter.sort(entities)

    def test_sortMongoCursorShouldPassTupleOfFieldNameAnd1ToCursorSort(self):
        fieldnames = [
            'age', 'username', 'some_random_fieldname'
        ]
        for fieldname in fieldnames:
            mockCursor = MagicMock()
            sorter = AscendingSorter(fieldname)
            
            cursor = sorter.sortMongoCursor(mockCursor)

            assert cursor == mockCursor
            mockCursor.sort.assert_called_with([ (fieldname, 1) ])

    def test_comparingEqualityOfSortersShouldProduceFalseWhenFieldsNotMatch(self):
        sorter1 = AscendingSorter('username')
        fieldnames = [
            'age', 'date', 'title', 'some_field'
        ]

        for field in fieldnames:
            sorter2 = AscendingSorter(field)

            assert not sorter1 == sorter2

    def test_comparingEqualityOfSortersShouldProduceTrueWhenFieldsMatch(self):
        sorter1 = AscendingSorter('username')
        sorter2 = AscendingSorter('username')

        assert sorter1 == sorter2

    def test_comparingEqualityAgainstSameFieldDescendingShouldProduceFalse(self):
        sorter1 = AscendingSorter('username')
        sorter2 = DescendingSorter('username')

        assert not sorter1 == sorter2


class TestDescendingSorter:
    def test_sortEntityShouldSortEntityBySpecifiedStringFieldInDescendingOrder(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = DescendingSorter('username')
        
        sorted_entity = sorter.sort(entities)

        assert sorted_entity == TEST_DATA['DESC_SORTED_BY_USERNAME']

    def test_sortEntityShouldSortEntityBySpecifiedNumberFieldInDescendingOrder(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = DescendingSorter('age')
        
        sorted_entity = sorter.sort(entities)

        assert sorted_entity == TEST_DATA['DESC_SORTED_BY_AGE']

    def test_sortEntityShouldRaiseExceptionWhenKeyNotExist(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = DescendingSorter('non_exist')
        
        with pytest.raises(FieldNotFoundInEntityError):
            sorter.sort(entities)

    def test_sortMongoCursorShouldPassTupleOfFieldNameAndMinus1ToCursorSort(self):
        fieldnames = [
            'age', 'username', 'some_random_fieldname'
        ]
        for fieldname in fieldnames:
            mockCursor = MagicMock()
            sorter = DescendingSorter(fieldname)
            
            cursor = sorter.sortMongoCursor(mockCursor)

            assert cursor == mockCursor
            mockCursor.sort.assert_called_with([ (fieldname, -1) ])
    
    def test_comparingEqualityOfSortersShouldProduceFalseWhenFieldsNotMatch(self):
        sorter1 = DescendingSorter('username')
        fieldnames = [
            'age', 'date', 'title', 'some_field'
        ]

        for field in fieldnames:
            sorter2 = DescendingSorter(field)

            assert not sorter1 == sorter2

    def test_comparingEqualityOfSortersShouldProduceTrueWhenFieldsMatch(self):
        sorter1 = DescendingSorter('username')
        sorter2 = DescendingSorter('username')

        assert sorter1 == sorter2

    def test_comparingEqualityAgainstSameFieldDescendingShouldProduceFalse(self):
        sorter1 = DescendingSorter('username')
        sorter2 = AscendingSorter('username')

        assert not sorter1 == sorter2


class TestNullSorter:
    def test_sortShouldNotDoAnything(self):
        entities = TEST_DATA['ENTITIES'].copy()
        sorter = NullSorter()
        
        sorted_entity = sorter.sort(entities)

        assert sorted_entity == entities
    
    def test_sortMongoCursorShouldNotCallSortOnCursor(self):
        mockCursor = MagicMock()
        sorter = NullSorter()
        
        cursor = sorter.sortMongoCursor(mockCursor)

        assert cursor == mockCursor
        assert mockCursor.sort.call_count == 0

    def test_shouldCompareTrueWhenOtherIsNullSorter(self):
        sorter1 = NullSorter()
        sorter2 = NullSorter()

        assert sorter1 == sorter2

    def test_shouldCompareFalseWhenOtherIsAscOrDescSorter(self):
        sorter1 = NullSorter()
        sorter2 = AscendingSorter('some_field')
        sorter3 = DescendingSorter('some_field')

        assert not sorter1 == sorter2
        assert not sorter1 == sorter3
