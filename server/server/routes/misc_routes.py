from flask import Blueprint, request, current_app, render_template, g, session, jsonify

# from server.middleware.session import SessionManager
import server.app_utils as app_utils
import server.routes.route_utils as route_utils

routes = Blueprint('miscRoutes', __name__)

@routes.route('/')
@routes.route('/index')
def hello_world():
    # currentUser = session.get('userId', 'None')
    # SessionManager.setCurrentUserFromSession(g, session)
    # return f'You have a userId of {currentUser}!'
    return 'hello world!'

@routes.route('/clear')
def clear():
    session.clear()
    return 'cleared!'

@routes.route('/jsonstring')
def jsonstring():
    json = r'{ "name": "Danny", "age": "13", "families": ["mother", "father", "sister"]}'
    return json

@routes.route('/template')
def template():
    return render_template('hello.html', user='default')

@routes.route('/template/<username>')
def template1(username):
    return render_template('hello.html', user=username)

@routes.route('/userlist', methods=['GET'])
def userlist():
    users = app_utils.getDB(current_app).searchUser([])
    for user in users:
        user.pop('_id', None)

    return route_utils.createJSONResponse( [ route_utils.createUsersObject(users) ], 200 )