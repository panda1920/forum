# -*- coding: utf-8 -*-
"""
This file houses configuration information for the main flask app
"""


import os
from pathlib import Path

from server.database.file_crudmanager import FileCrudManager
from server.database.mongo_crudmanager import MongoCrudManager
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.database.paging import Paging
from server.middleware.userauth import UserAuthentication
from server.services.entity_creation_service import EntityCreationService
from server.services.search_service import SearchService
from server.services.image_scaler import ImageScaler


class Config:
    # when using file-based db, this is where data gets stored
    DATA_LOCATION = os.environ.get('DATA_LOCATION')

    # define classes/objects that are referenced in the app
    # can be replaced during tests
    USER_AUTHENTICATION = UserAuthentication
    # DATABASE_REPOSITORY = FileCrudManager(Path(DATA_LOCATION), USER_AUTHENTICATION)
    DATABASE_REPOSITORY = MongoCrudManager(
        os.environ.get('MONGO_DBNAME', 'TEST_MYFORUMWEBAPP'),
        USER_AUTHENTICATION
    )
    SEARCH_FILTER = PrimitiveFilter
    AGGREGATE_FILTER = AggregateFilter
    PAGING = Paging

    # services
    CREATION_SERVICE = EntityCreationService(DATABASE_REPOSITORY, SEARCH_FILTER)
    SEARCH_SERVICE = SearchService(DATABASE_REPOSITORY, SEARCH_FILTER, AGGREGATE_FILTER, PAGING)
    IMAGE_SCALER = ImageScaler()

    # for session
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # define how long persisting session information would be held by client
    # PERMANENT_SESSION_LIFETIME = os.environ.get('')

    # cookies are only sent over SSL connection
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)
