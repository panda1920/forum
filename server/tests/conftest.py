# -*- coding: utf-8 -*-
"""
This file defines common test fixtures used across the project
"""
import pytest

from server import server

@pytest.fixture(scope='module')
def app():
    app = server.setupApp()
    yield app

@pytest.fixture(scope='function')
def client(app):
    with app.text_client() as client:
        yield client