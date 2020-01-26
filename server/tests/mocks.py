from unittest.mock import create_autospec

from flask import g, request, session

from server.database.crudmanager import CrudManager
from server.database.filter import Filter
from server.database.paging import Paging
from server.middleware.userauth import UserAuthentication
from server.middleware.signup import Signup

def createMockDB():
    return create_autospec(CrudManager)

def createMockFilter():
    return create_autospec(Filter)

def createMockPaging():
    return create_autospec(Paging)

def createMockUserAuth():
    return create_autospec(UserAuthentication)

def createMockSignup():
    return create_autospec(Signup)

def createMockRequest():
    return create_autospec(request, instance=True)

def createMockG():
    return create_autospec(g, instance=True)

def createMockSession(sessionInfo = {}):
    defaults = {
        'new': False,
        'modified': False,
        'permanent': False,
    }
    mock = {}
    mock.update(defaults)
    mock.update(sessionInfo)
    return mock