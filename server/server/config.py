import os
from pathlib import Path

from server.database.simplefile import SimpleFile
from server.database.filter import Filter
from server.database.paging import Paging

class Config:
    # when using file-based db, this is where data gets stored
    DATA_LOCATION = os.environ.get('DATA_LOCATION')

    # define classes/objects that are referenced in the app
    # can be replaced during tests
    DATABASE_OBJECT = SimpleFile(Path(DATA_LOCATION))
    SEARCH_FILTER = Filter
    PAGING = Paging

    # for session
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # define how long persisting session information would be held by client
    # PERMANENT_SESSION_LIFETIME = os.environ.get('')

    # for ssl
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)