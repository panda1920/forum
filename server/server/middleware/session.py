# -*- coding: utf-8 -*-
"""
This file houses session related operations
"""

from flask import g, session


class SessionManager:
    """
    A namespace to put all session related functions
    """
    ANONYMOUS_USERID = '0'

    @classmethod
    def setCurrentUserFromSession(cls, g, session):
        userId = session.get('userId', None)
        if userId is None:
            session['userId'] = cls.ANONYMOUS_USERID
            userId = cls.ANONYMOUS_USERID
        
        g.currentUser = {
            'userId': userId
        }

    @classmethod
    def setSessionUser(cls, user):
        session['userId'] = user['userId']
        cls.setCurrentUserFromSession(g, session)
