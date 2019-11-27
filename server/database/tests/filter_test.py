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
            'operator': FuzzyStringFilter.getOpString(),
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, FuzzyStringFilter)
    
    def test_createGT(self):
        querystringObj = {
            'operator': GTFilter.getOpString(),
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, GTFilter)
    
    def test_createGTE(self):
        querystringObj = {
            'operator': GTEFilter.getOpString(),
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, GTEFilter)
    
    def test_createLT(self):
        querystringObj = {
            'operator': LTFilter.getOpString(),
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, LTFilter)
    
    def test_creatLTE(self):
        querystringObj = {
            'operator': LTEFilter.getOpString(),
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, LTEFilter)
    
    def test_createEQ(self):
        querystringObj = {
            'operator': EQFilter.getOpString(),
            'value': [100],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, EQFilter)

    def test_createFilterShouldThrowExceptionWhenMissingAttributes(self):
        querystringObjs = [
            {'operator': EQFilter.getOpString(), 'value': [100]}, # missing field
            {'operator': EQFilter.getOpString(), 'field': 'content'}, # missing value
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
        f = self.createFilter(FuzzyStringFilter.getOpString(), ['is', 'as'])
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

        f = self.createFilter(GTFilter.getOpString())
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

        f = self.createFilter(GTEFilter.getOpString())
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

        f = self.createFilter(LTFilter.getOpString())
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

        f = self.createFilter(LTEFilter.getOpString())
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
        f = self.createFilter(EQFilter.getOpString(), [self.FIELD_VALUE, 500])
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