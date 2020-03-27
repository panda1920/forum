# -*- coding: utf-8 -*-
"""
This file houses session related service methods
"""
from server.entity.user import removePrivateInfo
from server.database.filter import PrimitiveFilter


class SessionService:
    """
    Provides methods that change the state of current session user.
    """
    SESSION_USER_KEY = 'sessionUser'
    ANONYMOUS_USER = dict(userId='0')

    def __init__(self, repo, flask_context):
        self._repo = repo
        self._context = flask_context

    def set_user(self, user):
        """
        Change session user to designated user.
        Change the current user in global context as well.
        
        Args:
            user(dict): user entity
        Returns:
            None
        """
        userId = user['userId']
        # want to keep session information as small as possible
        # which is why only userId info is stored in session
        self._context.write_session(self.SESSION_USER_KEY, dict(userId=userId))
        self.set_global_user(user)

    def remove_user(self):
        """
        Change session user to anonymous user.
        CHange the current user in global context as well.
        
        Args:
            None
        Returns:
            None
        """
        self.set_user(self.ANONYMOUS_USER)

    def set_global_user(self, user):
        """
        set current user in the global context to designated user.
        Performs query to the repository because this method requires
        complete information of user.
        
        Args:
            user(dict): user entity
        Returns:
            return value
        """
        searchFilter = PrimitiveFilter.createFilter(dict(
            field='userId', operator='eq', value=[ user['userId'] ]
        ))
        user_indb = self._repo.searchUser(searchFilter)['users'][0]

        self._context.write_global(self.SESSION_USER_KEY, removePrivateInfo(user_indb) )
