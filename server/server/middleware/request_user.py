# -*- coding: utf-8 -*-
"""
This file houses middleware to make session user info available to each requests
"""
import json


class RequestUserManager:
    """
    This class is responsible for providing functionality to
    make session user available for each incoming request.
    """
    def __init__(self, session_service):
        self._session = session_service

    def setCurrentUser(self):
        """
        Places information of session user in global
        Intended to be called in before_request hook.
        
        Args:
        Returns:
            None
        """
        self._session.populate_request_user()

    def addCurrentUserToResponse(self, response):
        """
        Add user information to response data that is sent back to client.
        Intended to be called in after_request.
        
        Args:
            response: response object of flask
        Returns:
            updated response object
        """
        current_user = self._session.get_user()
        response_data = json.loads( response.get_data() )
        response_data[self._session.REQUEST_USER_KEY] = current_user.to_serialize()

        response.set_data( json.dumps(response_data) )
        return response
