# -*- coding: utf-8 -*-
"""
This file contains fixtures for database related testing
"""

import pytest

@pytest.fixture(scope='module')
def createDB(request):
    """
    creates setup helper object for testing
    for this to work properly,
    make sure to specify which setup helper class to use by parametrizing fixture
    which replaces reuquest.param with the classname
    """
    DBToTest = request.param
    db = DBToTest()
    yield db
    db.teardown()

@pytest.fixture(scope='function')
def setupDB(createDB):
    """
    data creation/destruction used for each testcase
    returns the setup helper object that was created by createDB() fixture
    """
    createDB.setup()
    yield createDB
    createDB.cleanup()