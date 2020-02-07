# -*- coding: utf-8 -*-
"""
This file houses mocks used in tests
"""

from unittest.mock import create_autospec

from flask import g, request, session

from server.database.crudmanager import CrudManager
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.database.paging import Paging
from server.middleware.userauth import UserAuthentication
from server.services.search_service import SearchService
from server.services.entity_creation_service import EntityCreationService

def createMockDB():
    return create_autospec(CrudManager)

def createMockFilter():
    return create_autospec(PrimitiveFilter)

def createMockAggregateFilter():
    return create_autospec(AggregateFilter)

def createMockPaging():
    return create_autospec(Paging)

def createMockUserAuth():
    return create_autospec(UserAuthentication)

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

def createMockSearchService():
    return create_autospec(SearchService)

def createMockEntityCreationService():
    return create_autospec(EntityCreationService)