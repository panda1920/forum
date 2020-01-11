# -*- coding: utf-8 -*-
"""
This file defines common test fixtures used across the project
"""
import pytest

from server import server

@pytest.fixture(scope='module')
def app():
    app = server.setupApp()
    app.testing = True
    yield app