from unittest.mock import create_autospec

from flask import g, request

from server.database.database import Database
from server.database.filter import Filter
from server.database.paging import Paging

def createMockDB():
    return create_autospec(Database)

def createMockFilter():
    return create_autospec(Filter)

def createMockPaging():
    return create_autospec(Paging)

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