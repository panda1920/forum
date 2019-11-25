import os
from pathlib import Path

from server.database.simplefile import SimpleFile

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'this_is_secretkey')
    DATA_LOCATION = os.environ.get('DATA_LOCATION', r'E:\python\py3\repos\forum\server\data')
    DATABASE_OBJECT = SimpleFile(Path(DATA_LOCATION))