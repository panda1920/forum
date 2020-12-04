# -*- coding: utf-8 -*-
"""
This file defines common test fixtures and hooks used across the project
"""
import pytest

from server import server


@pytest.fixture(scope='module')
def app():
    app = server.setupApp()
    app.testing = True
    yield app

@pytest.fixture(scope='module')
def saveOldConfig(app):
    oldConf = app.config
    app.config = {**oldConf}
    
    yield

    app.config = oldConf
