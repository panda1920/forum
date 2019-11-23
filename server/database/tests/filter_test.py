import sys
from pathlib import Path
import pytest
import pdb

PROJECT_DIR = Path(__file__).resolve().parents[3]

sys.path.append( str(PROJECT_DIR / 'server') )
from database.filter import *

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
            'operator': 'fuzzy',
            'value': ['val1'],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, EQFilter)
  
    def test_createPage(self):
        querystringObj = {
            'operator': 'page',
            'value': ['val1'],
            'field': 'content',
        }
        f = Filter.createFilter(querystringObj)

        assert isinstance(f, PageFilter)

class TestFilterMatching:
    pass