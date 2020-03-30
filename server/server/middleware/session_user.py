# -*- coding: utf-8 -*-
"""
This file houses middleware to make session user info available to each requests
"""
import json


class SessionUserManager:
    """
    This class holds methods that deal with session user.
    Session user information is typically handled before and after every request.
    """
    def __init__(self, session_service, flask_context):
        self._session = session_service
        self._context = flask_context

    def setCurrentUser(self):
        """
        Places information of session user in global
        
        Args:
        Returns:
            None
        """
        session_user = self._context.read_session(self._session.SESSION_USER_KEY)
        if session_user is None:
            session_user = self._session.ANONYMOUS_USER

        self._session.set_global_user(session_user)

    def addCurrentUserToResponse(self, response):
        """
        Add session user information to response data that is sent back to client.
        Intended to be called in after_request.
        
        Args:
            response: response object of flask
        Returns:
            update response object
        """
        session_user = self._context.read_global(self._session.SESSION_USER_KEY)
        response_data = json.loads( response.get_data() )
        response_data[self._session.SESSION_USER_KEY] = session_user

        response.set_data( json.dumps(response_data) )
        return response
