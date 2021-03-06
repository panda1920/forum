# -*- coding: utf-8 -*-
"""
This file houses mocks used in tests
"""

from unittest.mock import create_autospec

from flask import g, request

from server.database.crudmanager import CrudManager
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.database.paging import Paging
from server.services.userauth import UserAuthenticationService, PasswordService
from server.services.entity_creation_service import EntityCreationService
from server.services.search_service import SearchService
from server.services.update_service import UpdateService
from server.services.delete_service import DeleteService
from server.services.session import SessionService
from server.services.flask_context import FlaskContext
from server.services.image_scaler import ImageScalerBase
from server.entity import Entity
from server.middleware.request_user import RequestUserManager
from server.services.searchfilter_creator import SearchFilterCreator


def createMockRepo():
    return create_autospec(CrudManager)


def createMockFilter():
    return create_autospec(PrimitiveFilter)


def createMockAggregateFilter():
    return create_autospec(AggregateFilter)


def createMockPaging():
    return create_autospec(Paging)


def createMockUserAuth():
    return create_autospec(UserAuthenticationService)


def createMockPassword():
    return create_autospec(PasswordService)


def createMockRequest():
    return create_autospec(request, instance=True)


def createMockG():
    return create_autospec(g, instance=True)


def createMockRequestUserManager():
    return create_autospec(RequestUserManager)


def createMockFlaskContext():
    return create_autospec(FlaskContext)


def createMockSearchService():
    return create_autospec(SearchService)


def createMockEntityCreationService():
    return create_autospec(EntityCreationService)


def createMockUpdateService():
    return create_autospec(UpdateService)


def createMockDeleteService():
    return create_autospec(DeleteService)


def createMockSessionService():
    return create_autospec(SessionService)


def createMockImageScaler():
    return create_autospec(ImageScalerBase)


def createMockEntity():
    return create_autospec(Entity)


def createMockSearchFilterCreatorService():
    return create_autospec(SearchFilterCreator)
