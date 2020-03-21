# -*- coding: utf-8 -*-
"""
This file houses session related operations
"""
import json

import server.entity.user as user


class SessionUserManager:
    """
    This class holds methods that deal with session user.
    Session user information is typically handled before and after every request.
    """
    ANONYMOUS_USER = {
        'userId': '0'
    }
    SESSION_USER_KEY = 'sessionUser'

    def __init__(self, search_service, flask_context):
        self._search = search_service
        self._context = flask_context

    def setCurrentUser(self):
        """
        Places information of session user in flask.g
        
        Args:
        Returns:
            None
        """
        session_user = self._context.read_session(self.SESSION_USER_KEY)
        if session_user is None:
            session_user = self.ANONYMOUS_USER

        result = self._search.searchUsersByKeyValues(dict(userId=session_user['userId']))
        user_info = user.removePrivateInfo( result['users'][0] )

        self._context.write_global(self.SESSION_USER_KEY, user_info)

    def setSessionUser(self, user):
        """
        Change session user.
        Intended to be called after successful login attempt.
        
        Args:
            user(dict): user that logged in
        Returns:
            None
        """
        userId = user['userId']
        self._context.write_session(self.SESSION_USER_KEY, dict(userId=userId))
        self.setCurrentUser()

    def removeSessionUser(self):
        """
        Removes user information in session.
        Intended to be called during logout attempt.
        
        Args:
            None
        Returns:
            None
        """
        self._context.write_session(self.SESSION_USER_KEY, self.ANONYMOUS_USER)
        self.setCurrentUser()

    def addCurrentUserToResponse(self, response):
        """
        Add session user information to response data that is sent back to client.
        Intended to be called in after_request.
        
        Args:
            response: response object of flask
        Returns:
            None
        """
        session_user = self._context.read_global(self.SESSION_USER_KEY)
        response_data = json.loads( response.get_data() )
        response_data[self.SESSION_USER_KEY] = session_user

        response.set_data( json.dumps(response_data) )