# -*- coding: utf-8 -*-
#
# This file contains fixtures for database related testing
#

import pytest

@pytest.fixture(scope='module')
def createDB(request):
    # specify which setup helper class to use by parametrizing fixture
    DBToTest = request.param
    db = DBToTest()
    yield db
    db.teardown()

@pytest.fixture(scope='function')
def setupDB(createDB):
    createDB.setup()
    yield createDB
    createDB.cleanup()