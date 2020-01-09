import os
from pathlib import Path

from server.database.simplefile import SimpleFile
from server.database.filter import Filter
from server.database.paging import Paging

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'this_is_secretkey')
    DATA_LOCATION = os.environ.get('DATA_LOCATION', r'E:\python\py3\repos\forum\server\server\data')
    DATABASE_OBJECT = SimpleFile(Path(DATA_LOCATION))
    SEARCH_FILTER = Filter
    PAGING = Paging