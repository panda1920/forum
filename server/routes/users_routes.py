import urllib.parse

from flask import Blueprint, request, current_app, make_response

import server.routes.routes_util as util
from server.database.filter import Filter
from server.database.paging import Paging
from server.exceptions import MyAppException

routes = Blueprint('userRoutes', __name__)

@routes.route('/v1/users', methods=['GET'])
def searchUserv1():
    # do i need this api?
    try:
        searchCriteria = util.createSearchFilters(request.args, fieldName='userName')
        users = util.getDB().searchUser(searchCriteria)
    except MyAppException as e:
        return util.createJSONErrorResponse(e)
    
    return util.createJSONResponse([ util.createUsersObject(users) ], 200)

@routes.route('/v1/users/<userId>', methods=['GET'])
def searchUserByIDv1(userId):
    try:
        searchCriteria = util.createIDFilters(fieldName='userId', idValue=userId)
        users = util.getDB().searchUser(searchCriteria)
    except MyAppException as e:
        return util.createJSONErrorResponse(e)

    return util.createJSONResponse([ util.createUsersObject(users) ], 200)

@routes.route('/v1/users/create', methods=['POST'])
def createUserv1():
    userProperties = request.form
    try:
        util.getDB().createUser(userProperties)
    except MyAppException as e:
        return util.createJSONErrorResponse(e)

    return util.createJSONResponse([], 200)

@routes.route('/v1/users/<userId>/update', methods=['PATCH'])
def updateUserv1(userId):
    try:
        userData = util.getJsonFromRequest(request)
        userData.update({ 'userId': userId })
        util.getDB().updateUser(userData)
    except MyAppException as e:
        return util.createJSONErrorResponse(e)

    return util.createJSONResponse([], 200)

@routes.route('/v1/users/<userId>/delete', methods=['DELETE'])
def deleteUserv1(userId):
    try:
        util.getDB().deleteUser([userId])
    except MyAppException as e:
        return util.createJSONErrorResponse(e)

    return util.createJSONResponse([], 200)