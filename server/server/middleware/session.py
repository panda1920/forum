import server.app_utils as app_utils
import server.routes.route_utils  as route_utils 
import server.exceptions as exceptions

class SessionManager:
    """
    A namespace to put all session related functions
    """
    ANONYMOUS_USERID = '0'
    @staticmethod
    def setCurrentUserFromSession(g, session):
        userId = session.get('userId', None)
        if userId == None:
            session['userId'] = SessionManager.ANONYMOUS_USERID
            userId = SessionManager.ANONYMOUS_USERID
        
        g.currentUser = {
            'userId': userId
        }