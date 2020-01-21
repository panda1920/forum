import os
from pathlib import Path

from server.database.file_crudmanager import FileCrudManager
from server.database.filter import Filter
from server.database.paging import Paging
from server.middleware.userauth import UserAuthentication

class Config:
    # when using file-based db, this is where data gets stored
    DATA_LOCATION = os.environ.get('DATA_LOCATION')

    # define classes/objects that are referenced in the app
    # can be replaced during tests
    USER_AUTHENTICATION = UserAuthentication
    DATABASE_OBJECT = FileCrudManager(Path(DATA_LOCATION), USER_AUTHENTICATION)
    SEARCH_FILTER = Filter
    PAGING = Paging

    # for session
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # define how long persisting session information would be held by client
    # PERMANENT_SESSION_LIFETIME = os.environ.get('')

    # cookies are only sent over SSL connection
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)