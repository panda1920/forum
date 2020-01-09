import pytest

import server.app_utils as app_utils
import server.routes.route_utils  as route_utils 
import server.exceptions as exceptions

class SessionManager:
    """
    A namespace to put all session related functions
    """
    @staticmethod
    def setCurrentUserFromSession(g, session):
        if session['new']:
            userId = '0'
            session['userId'] = '0'
        else:
            try:
                userId = session['userId']
            except:
                raise exceptions.InvalidSession('Invalid session')
        
        g.currentUser = {
            'userId': userId
        }