# -*- coding: utf-8 -*-
"""
This file houses configuration information for the main flask app
"""

import os
# from pathlib import Path

# from server.database.file_crudmanager import FileCrudManager
from server.database.mongo_crudmanager import MongoCrudManager
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.database.paging import Paging
from server.services.flask_context import FlaskContext
from server.services.userauth import UserAuthentication
from server.services.entity_creation_service import EntityCreationService
from server.services.search_service import SearchService
from server.services.update_service import UpdateService
from server.services.delete_service import DeleteService
from server.services.image_scaler import ImageScaler
from server.middleware.session_user import SessionUserManager

# object initialization
repo = MongoCrudManager(
    os.environ.get('MONGO_DBNAME', 'TEST_MYFORUMWEBAPP'),
    UserAuthentication
)
# repo = FileCrudManager(Path(DATA_LOCATION), USER_AUTHENTICATION)
flask_context = FlaskContext()
creation_service = EntityCreationService(repo, PrimitiveFilter)
search_service = SearchService(repo, PrimitiveFilter, AggregateFilter, Paging)
update_service = UpdateService(repo, PrimitiveFilter)
delete_service = DeleteService(repo, flask_context)
image_scaler = ImageScaler()
session_user = SessionUserManager(search_service, flask_context)
user_authentication = UserAuthentication(repo, PrimitiveFilter, session_user)


class Config:
    # when using file-based db, this is where data gets stored
    DATA_LOCATION = os.environ.get('DATA_LOCATION')

    # define classes/objects that are referenced in the app
    # can be replaced during tests

    DATABASE_REPOSITORY = repo
    SEARCH_FILTER = PrimitiveFilter
    AGGREGATE_FILTER = AggregateFilter
    PAGING = Paging

    # services
    FLASK_CONTEXT = flask_context
    CREATION_SERVICE = creation_service
    SEARCH_SERVICE = search_service
    UPDATE_SERVICE = update_service
    DELETE_SERVICE = delete_service
    IMAGE_SCALER = image_scaler
    USER_AUTHENTICATION = user_authentication

    # middlewares
    SESSION_USER = session_user

    # for session
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # define how long persisting session information would be held by client
    # PERMANENT_SESSION_LIFETIME = os.environ.get('')

    # cookies are only sent over SSL connection
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', True)

    # methods to extract config from app

    @staticmethod
    def getDB(app):
        return app.config['DATABASE_REPOSITORY']

    @staticmethod
    def getFilter(app):
        return app.config['SEARCH_FILTER']

    @staticmethod
    def getAggregateFilter(app):
        return app.config['AGGREGATE_FILTER']

    @staticmethod
    def getPaging(app):
        return app.config['PAGING']

    @staticmethod
    def getUserAuth(app):
        return app.config['USER_AUTHENTICATION']

    @staticmethod
    def getFlaskContext(app):
        return app.config['FLASK_CONTEXT']

    @staticmethod
    def getCreationService(app):
        return app.config['CREATION_SERVICE']
    
    @staticmethod
    def getSearchService(app):
        return app.config['SEARCH_SERVICE']

    @staticmethod
    def getUpdateService(app):
        return app.config['UPDATE_SERVICE']

    @staticmethod
    def getDeleteService(app):
        return app.config['DELETE_SERVICE']

    @staticmethod
    def getImageScaler(app):
        return app.config['IMAGE_SCALER']

    @staticmethod
    def getSessionUser(app):
        return app.config['SESSION_USER']
