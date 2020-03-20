# -*- coding: utf-8 -*-
"""
This file houses session related operations
"""
import json


class SessionUserManager:
    """
    This class deals with session user information before and after every request
    """
    ANONYMOUS_USER = {
        'userId': '0'
    }
    SESSION_USER_KEY = 'sessionUser'

    def __init__(self, search_service, flask_context):
        self._search = search_service
        self._context = flask_context

    def setCurrentUser(self):
        session_user = self._context.read_session(self.SESSION_USER_KEY)
        if session_user is None:
            session_user = self.ANONYMOUS_USER

        result = self._search.searchUsersByKeyValues(dict(userId=session_user['userId']))

        self._context.write_global(self.SESSION_USER_KEY, result['users'][0])

    def setSessionUser(self, user):
        userId = user['userId']
        self._context.write_session(self.SESSION_USER_KEY, dict(userId=userId))

    def addCurrentUserToResponse(self, response):
        session_user = self._context.read_global(self.SESSION_USER_KEY)

        response_data = json.loads( response.get_data() )
        response_data[self.SESSION_USER_KEY] = session_user
        response.set_data( json.dumps(response_data) )