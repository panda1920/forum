# -*- coding: utf-8 -*-
"""
This file houses session related operations
"""


class SessionManager:
    """
    A namespace to put all session related functions
    """
    ANONYMOUS_USERID = '0'
    @staticmethod
    def setCurrentUserFromSession(g, session):
        userId = session.get('userId', None)
        if userId is None:
            session['userId'] = SessionManager.ANONYMOUS_USERID
            userId = SessionManager.ANONYMOUS_USERID
        
        g.currentUser = {
            'userId': userId
        }
