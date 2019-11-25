import pdb
import pytest

from server.database.filter import *
from server.exceptions import FilterParseError, InvalidOperatorError

@pytest.fixture(scope='function')
def fixture():
    pass

class TestFilterCreation:
    def test_createFuzzyString(self):
        querystringObj = {
            'operator': 'fuzzy',
            'value': ['val1'],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, FuzzyStringFilter)
    
    def test_createGT(self):
        querystringObj = {
            'operator': 'gt',
            'value': 100,
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, GTFilter)
    
    def test_createGTE(self):
        querystringObj = {
            'operator': 'gte',
            'value': 100,
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, GTEFilter)
    
    def test_createLT(self):
        querystringObj = {
            'operator': 'lt',
            'value': 100,
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, LTFilter)
    
    def test_creatLTE(self):
        querystringObj = {
            'operator': 'lte',
            'value': 100,
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, LTEFilter)
    
    def test_createEQ(self):
        querystringObj = {
            'operator': 'eq',
            'value': ['val1'],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, EQFilter)

    def test_createFilterShouldThrowExceptionWhenMissingAttributes(self):
        querystringObjs = [
            {'operator': 'eq', 'value': [1, 2]}, # missing field
            {'operator': 'eq', 'field': 'content'}, # missing value
            {'value': [1, 2], 'field': 'content'}, # missing operator
        ]

        with pytest.raises(FilterParseError):
            for querystringObj in querystringObjs:
                Filter.createFilter(querystringObj)

    def test_createFilterThrowsErrorWhenInvalidOperator(self):
        querystringObj = {
            'operator': 'non_existant_operator',
            'value': ['val1'],
            'field': 'content',
        }

        with pytest.raises(InvalidOperatorError):
            Filter.createFilter(querystringObj)

class TestFilterMatching:
    pass