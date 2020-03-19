# -*- coding: utf-8 -*-
"""
This file houses tests for flask_context.py
"""


import pytest

from flask import session, g

from server.services.flask_context import FlaskContext
import server.exceptions as exceptions


@pytest.fixture(scope='function', autouse=True)
def request_context(app):
    with app.test_request_context():
        yield


@pytest.fixture(scope='function')
def context():
    return FlaskContext()


class TestFlaskContextCrudGlobals:
    DEFAULT_KEY = 'currentUser'
    DEFAULT_VALUE = dict(
        userId='11223344',
        userName='sampleuser@myforumwebapp.com',
    )

    def test_write_globalShouldReflectChangeOnFlaskGlobal(self, context):
        context.write_global(self. DEFAULT_KEY, self.DEFAULT_VALUE)

        assert g.get(self.DEFAULT_KEY) == self.DEFAULT_VALUE

    def test_write_globalShouldUpdateAlreadySetValue(self, context):
        setattr(g, self.DEFAULT_KEY, 'hello')
        assert g.get(self.DEFAULT_KEY) == 'hello'

        context.write_global(self.DEFAULT_KEY, self.DEFAULT_VALUE)

        assert g.get(self.DEFAULT_KEY) == self.DEFAULT_VALUE

    def test_read_globalShouldRetrieveValueFromFlaskGlobal(self, context):
        setattr(g, self.DEFAULT_KEY, self.DEFAULT_VALUE)

        value = context.read_global(self.DEFAULT_KEY)

        assert value == self.DEFAULT_VALUE

    def test_read_globalShouldRaiseExceptionWhenKeyNotFound(self, context):
        with pytest.raises(exceptions.ValueNotFoundOnContext):
            context.read_global(self.DEFAULT_KEY)

    def test_delete_globalShouldRemoveKeyFromFlaskGlobal(self, context):
        setattr(g, self.DEFAULT_KEY, self.DEFAULT_VALUE)

        context.delete_global(self.DEFAULT_KEY)

        assert g.get(self.DEFAULT_KEY) is None

    def test_delete_globalOnNonExistingKeyShouldNotRaiseException(self, context):
        assert g.get(self.DEFAULT_KEY) is None
        
        context.delete_global(self.DEFAULT_KEY)

        assert g.get(self.DEFAULT_KEY) is None


class TestFlaskContextCrudSession:
    DEFAULT_KEY = 'currentUser'
    DEFAULT_VALUE = dict(
        userId='11223344',
        userName='sampleuser@myforumwebapp.com',
    )

    def test_write_sessionShouldReflectChangeOnFlaskGlobal(self, context):
        context.write_session(self. DEFAULT_KEY, self.DEFAULT_VALUE)

        assert session.get(self.DEFAULT_KEY) == self.DEFAULT_VALUE

    def test_write_sessionShouldUpdateAlreadySetValue(self, context):
        session[self.DEFAULT_KEY] = 'hello'
        assert session[self.DEFAULT_KEY] == 'hello'

        context.write_session(self.DEFAULT_KEY, self.DEFAULT_VALUE)

        assert session.get(self.DEFAULT_KEY) == self.DEFAULT_VALUE

    def test_write_sessionShouldFlagModified(self, context):
        context.write_session(self. DEFAULT_KEY, self.DEFAULT_VALUE)

        assert session.modified is True

    def test_read_sessionShouldRetrieveValueFromFlaskGlobal(self, context):
        session[self.DEFAULT_KEY] = self.DEFAULT_VALUE

        value = context.read_session(self.DEFAULT_KEY)

        assert value == self.DEFAULT_VALUE

    def test_read_sessionShouldRaiseExceptionWhenKeyNotFound(self, context):
        with pytest.raises(exceptions.ValueNotFoundOnContext):
            context.read_session(self.DEFAULT_KEY)

    def test_delete_sessionShouldRemoveKeyFromFlaskGlobal(self, context):
        session[self.DEFAULT_KEY] = self.DEFAULT_VALUE

        context.delete_session(self.DEFAULT_KEY)

        assert session.get(self.DEFAULT_KEY, None) is None

    def test_delete_sessionOnNonExistingKeyShouldNotRaiseException(self, context):
        assert session.get(self.DEFAULT_KEY, None) is None
        
        context.delete_session(self.DEFAULT_KEY)

        assert session.get(self.DEFAULT_KEY, None) is None
