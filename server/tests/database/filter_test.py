import pdb
import pytest

from server.database.filter import *
from server.exceptions import FilterParseError, InvalidFilterOperatorError

@pytest.fixture(scope='function')
def fixture():
    pass

class TestFilterCreation:
    def test_createFuzzyString(self):
        querystringObj = {
            'operator': 'fuzzy',
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, FuzzyStringFilter)
    
    def test_createGT(self):
        querystringObj = {
            'operator': 'gt',
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, GTFilter)
    
    def test_createGTE(self):
        querystringObj = {
            'operator': 'gte',
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, GTEFilter)
    
    def test_createLT(self):
        querystringObj = {
            'operator': 'lt',
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, LTFilter)
    
    def test_creatLTE(self):
        querystringObj = {
            'operator': 'lte',
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, LTEFilter)
    
    def test_createEQ(self):
        querystringObj = {
            'operator': 'eq',
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, EQFilter)

    def test_createFilterShouldThrowExceptionWhenMissingAttributes(self):
        querystringObjs = [
            {'operator': 'eq', 'value': [100]}, # missing field
            {'operator': 'eq', 'field': 'content'}, # missing value
            {'value': [100], 'field': 'content'}, # missing operator
        ]

        with pytest.raises(FilterParseError):
            for querystringObj in querystringObjs:
                Filter.createFilter(querystringObj)

    def test_createFilterThrowsErrorWhenInvalidOperator(self):
        querystringObj = {
            'operator': 'non_existant_operator',
            'value': [100],
            'field': 'content',
        }

        with pytest.raises(InvalidFilterOperatorError):
            Filter.createFilter(querystringObj)

class TestFilterMatching:
    FIELD_TO_COMPARE = 'counter'
    FIELD_VALUE = 100

    def test_fuzzyStringMatching(self):
        objsShouldMatch = [
            {self.FIELD_TO_COMPARE: 'is'},
            {self.FIELD_TO_COMPARE: 'his'},
            {self.FIELD_TO_COMPARE: 'history'},
            {self.FIELD_TO_COMPARE: 'I play bass'},
            {self.FIELD_TO_COMPARE: 'Fast fish'},
            {self.FIELD_TO_COMPARE: 'I made a mistake'},
            {self.FIELD_TO_COMPARE: 'I made a mistake', 'id': '11223344'},
        ]
        objsShouldNotMatch = [
            {self.FIELD_TO_COMPARE: 'aa'},
            {self.FIELD_TO_COMPARE: 'i s'},
            {self.FIELD_TO_COMPARE: '  i s '},
            {self.FIELD_TO_COMPARE: 'HISTORY'},
            {self.FIELD_TO_COMPARE: 'MASSAGE'},
            {self.FIELD_TO_COMPARE: 'I love testing'},
            {'id': '112233'},
            {'id': 'is'},
        ]

        # fuzzy search for 'is' OR 'as'
        f = self.createFilter('fuzzy', ['is', 'as'])
        for obj in objsShouldMatch:
            assert f.matches(obj)
        for obj in objsShouldNotMatch:
            assert not f.matches(obj)

    def test_GTFilter(self):
        objsShouldMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 10000},
        ]
        objsShouldNotMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 10000},
            {'id': '112233'},
            {'id': self.FIELD_VALUE + 1},
        ]

        f = self.createFilter('gt')
        for obj in objsShouldMatch:
            assert f.matches(obj)
        for obj in objsShouldNotMatch:
            assert not f.matches(obj)

    def test_GTEFilter(self):
        objsShouldMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 10000},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE},
        ]
        objsShouldNotMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 10000},
            {'id': '112233'},
            {'id': self.FIELD_VALUE + 1},
        ]

        f = self.createFilter('gte')
        for obj in objsShouldMatch:
            assert f.matches(obj)
        for obj in objsShouldNotMatch:
            assert not f.matches(obj)
            
    def test_LTFilter(self):
        objsShouldMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 10000},
        ]
        objsShouldNotMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 10000},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE},
            {'id': '112233'},
            {'id': self.FIELD_VALUE + 1},
        ]

        f = self.createFilter('lt')
        for obj in objsShouldMatch:
            assert f.matches(obj)
        for obj in objsShouldNotMatch:
            assert not f.matches(obj)

    def test_LTEFilter(self):
        objsShouldMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 10000},
        ]
        objsShouldNotMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 10000},
            {'id': '112233'},
            {'id': self.FIELD_VALUE + 1},
        ]

        f = self.createFilter('lte')
        for obj in objsShouldMatch:
            assert f.matches(obj)
        for obj in objsShouldNotMatch:
            assert not f.matches(obj)

    def test_EQFilter(self):
        objsShouldMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE},
            {self.FIELD_TO_COMPARE: 500},
        ]
        objsShouldNotMatch = [
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE - 10000},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 1},
            {self.FIELD_TO_COMPARE: self.FIELD_VALUE + 10000},
            {self.FIELD_TO_COMPARE: 500 + 10000},
            {self.FIELD_TO_COMPARE: 500 - 1},
            {'id': '112233'},
            {'id': self.FIELD_VALUE},
        ]

        # search for either of the 2 by exact matches
        f = self.createFilter('eq', [self.FIELD_VALUE, 500])
        for obj in objsShouldMatch:
            assert f.matches(obj)
        for obj in objsShouldNotMatch:
            assert not f.matches(obj)
    
    def createFilter(self, *args):
        op = args[0]
        fieldValue = args[1] if len(args) > 1 else [self.FIELD_VALUE]
        
        return Filter.createFilter(
            {
            'operator': op,
            'field': self.FIELD_TO_COMPARE,
            'value': fieldValue,
            }
        )

class TestFilterComparison:
    DEFAULT_FIELD = 'default_field'
    DEFAULT_FIELD_VALUES = [1, 2, 3]

    def createFilter(self, *args):
        op = args[0]
        field = args[1] if len(args) > 1 else self.DEFAULT_FIELD
        fieldValue = args[2:] if len(args) > 2 else self.DEFAULT_FIELD_VALUES
        
        return Filter.createFilter(
            {
            'operator': op,
            'field': field,
            'value': fieldValue,
            }
        )

    def test_EQFilterEquality(self):
        eqfilter1 = self.createFilter('eq')
        eqfilter2 = self.createFilter('eq')

        assert eqfilter1 == eqfilter2
        
    def test_EQFilterNonEquality(self):
        eqfilter1 = self.createFilter('eq')
        eqfilter2 = self.createFilter('eq', 'other_field')
        eqfilter3 = self.createFilter('eq', self.DEFAULT_FIELD, 1, 2)
        fuzzyfilter1 = self.createFilter('fuzzy')

        assert eqfilter1 != eqfilter2
        assert eqfilter1 != eqfilter3
        assert eqfilter2 != eqfilter3
        assert eqfilter1 != fuzzyfilter1

    def testFuzzyFilterEquality(self):
        fuzzyfilter1 = self.createFilter('fuzzy')
        fuzzyfilter2 = self.createFilter('fuzzy')

        assert fuzzyfilter1 == fuzzyfilter2

    def testFuzzyFilterNonEquality(self):
        fuzzyfilter1 = self.createFilter('fuzzy')
        fuzzyfilter2 = self.createFilter('fuzzy', 'other_field')
        fuzzyfilter3 = self.createFilter('fuzzy', self.DEFAULT_FIELD, 1, 2)
        eqfilter1 = self.createFilter('eq')

        assert fuzzyfilter1 != fuzzyfilter2
        assert fuzzyfilter1 != fuzzyfilter3
        assert fuzzyfilter2 != fuzzyfilter3
        assert fuzzyfilter1 != eqfilter1