# -*- coding: utf-8 -*-
"""
This file houses configuration information for the main flask app
"""

import os
from datetime import timedelta
# from pathlib import Path

# from server.database.file_crudmanager import FileCrudManager
from server.database.mongo_crudmanager import MongoCrudManager
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.database.paging import Paging
from server.database.file_repository import S3FileRepository
from server.services.flask_context import FlaskContext
from server.services.userauth import PasswordService, UserAuthenticationService
from server.services.entity_creation_service import EntityCreationService
from server.services.search_service import SearchService
from server.services.update_service import UpdateService
from server.services.delete_service import DeleteService
from server.services.session import SessionService
from server.services.image_scaler import ImageScaler
from server.services.searchfilter_creator import SearchFilterCreator
from server.services.portrait_uploader import PortraitUploader
from server.middleware.request_user import RequestUserManager

# object initialization
repo = MongoCrudManager(
    os.environ.get('MONGO_DBNAME', 'TEST_MYFORUMWEBAPP'),
    PasswordService,
)
# repo = FileCrudManager(Path(DATA_LOCATION), AUTHENTICATION_SERVICE)
file_repo = S3FileRepository( os.environ.get('AWS_S3_BUCKET_NAME') )
flask_context = FlaskContext()
session_service = SessionService(repo, flask_context)
request_user = RequestUserManager(session_service)
image_scaler = ImageScaler()
portrait_uploader = PortraitUploader(session_service, file_repo)
authentication_service = UserAuthenticationService(repo, session_service)
creation_service = EntityCreationService(repo, PrimitiveFilter, session_service)
search_service = SearchService(repo, SearchFilterCreator, PrimitiveFilter, AggregateFilter, Paging)
update_service = UpdateService(repo, PrimitiveFilter, session_service, portrait_uploader)
delete_service = DeleteService(repo, session_service)


class Config:
    # when using file-based db, this is where data gets stored
    DATA_LOCATION = os.environ.get('DATA_LOCATION')

    # define classes/objects that are referenced in the app
    # can be replaced during tests

    DATABASE_REPOSITORY = repo
    FILE_REPOSITORY = file_repo
    SEARCH_FILTER = PrimitiveFilter
    AGGREGATE_FILTER = AggregateFilter
    SEARCH_FILTER_CREATOR = SearchFilterCreator
    PAGING = Paging

    # services
    FLASK_CONTEXT = flask_context
    SESSION_SERVICE = session_service
    CREATION_SERVICE = creation_service
    SEARCH_SERVICE = search_service
    UPDATE_SERVICE = update_service
    DELETE_SERVICE = delete_service
    PORTRAIT_UPLOAD_SERVICE = portrait_uploader
    IMAGE_SCALER = image_scaler
    AUTHENTICATION_SERVICE = authentication_service
    PASSWORD_SERVICE = PasswordService

    # middlewares
    REQUESTUSER_MIDDLEWARE = request_user

    # for session
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # define how long session information would be held by client
    # PERMANENT_SESSION_LIFETIME = os.environ.get('')
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)

    # cookies are only sent over SSL connection
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)

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
    def getAuthService(app):
        return app.config['AUTHENTICATION_SERVICE']

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
    def getSessionService(app):
        return app.config['SESSION_SERVICE']

    @staticmethod
    def getImageScaler(app):
        return app.config['IMAGE_SCALER']

    @staticmethod
    def getRequestUserManager(app):
        return app.config['REQUESTUSER_MIDDLEWARE']
