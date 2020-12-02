# -*- coding: utf-8 -*-
"""
This file houses session related service methods
"""
import logging

from server.database.filter import PrimitiveFilter

logger = logging.getLogger(__name__)


class SessionService:
    """
    Provides methods that interacts with current session user.
    """
    SESSION_USER_KEY = 'sessionUserId'
    REQUEST_USER_KEY = 'sessionUser'
    ANONYMOUS_USERID = '0'

    def __init__(self, repo, flask_context):
        self._repo = repo
        self._context = flask_context

    def set_user(self, user):
        """
        Change session user to designated user.
        Change the current user in request context as well.
        
        Args:
            user(dict): user entity
        Returns:
            None
        """
        logger.info('Setting session user')
        self._context.write_session(self.SESSION_USER_KEY, user.userId)
        self._context.write_global(self.REQUEST_USER_KEY, user)

    def remove_user(self):
        """
        Change session user to anonymous user.
        CHange the current user in request context as well.
        
        Args:
            None
        Returns:
            None
        """
        logger.info('Removing session user')
        anonymous = self._find_user(self.ANONYMOUS_USERID)
        self.set_user(anonymous)

    def get_user(self):
        """
        Reads user information from current request context.
        Intended to be used in situations where authorizations are required.
        
        Args:
        Returns:
            user dict
        """
        logger.info('Reading user from request context')
        return self._context.read_global(self.REQUEST_USER_KEY)

    def populate_request_user(self):
        """
        Popualtes request context user based on session user.
        Anonymous user is set if no session found.
        
        Args:
            None
        Returns:
            None
        """
        logger.info('Populating user information in request context')
        session_userid = self._context.read_session(self.SESSION_USER_KEY)
        if session_userid is None:
            user = self._find_user(self.ANONYMOUS_USERID)
        else:
            user = self._find_user(session_userid)

        self._context.write_global(self.REQUEST_USER_KEY, user)

    def _find_user(self, userid):
        search_filter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ userid ]
        ))
        return self._repo.searchUser(search_filter)['users'][0]
