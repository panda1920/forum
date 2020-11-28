from flask import Blueprint, session

routes = Blueprint('miscRoutes', __name__)


@routes.route('/', methods=['GET'])
@routes.route('/index', methods=['GET'])
def hello_world():
    # currentUser = session.get('userId', 'None')
    # RequestUserManager.setCurrentUserFromSession(g, session)
    # return f'You have a userId of {currentUser}!'
    return 'hello world!'


@routes.route('/clear')
def clear():
    session.clear()
    return 'cleared!'


@routes.route('/health')
def health():
    return 'healthy'
