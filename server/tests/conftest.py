# -*- coding: utf-8 -*-
"""
This file defines common test fixtures and hooks used across the project
"""
import os

import pytest

from server import server


def pytest_configure(config):
    # sets environment variable for tests
    os.environ['ENV'] = 'TEST'
    os.environ['MONGO_HOSTNAME'] = 'localhost'
    os.environ['MONGO_PORT'] = '3000'
    return config

@pytest.fixture(scope='module')
def app():
    app = server.setupApp()
    app.testing = True
    yield app

@pytest.fixture(scope='function')
def saveOldConfig(app):
    oldConf = app.config
    app.config = {**oldConf}
    
    yield

    app.config = oldConf
