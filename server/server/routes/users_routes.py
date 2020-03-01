# -*- coding: utf-8 -*-
"""
This file houses routes for user related api
"""

from flask import Blueprint, request, current_app

from server.config import Config
import server.routes.route_utils as route_utils
from server.exceptions import MyAppException

routes = Blueprint('userRoutes', __name__)


@routes.route('/v1/users', methods=['GET'])
def searchUserv1():
    try:
        search = Config.getSearchService(current_app)
        result = search.searchUsersByKeyValues( request.args.to_dict(flat=True) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@routes.route('/v1/users/<userId>', methods=['GET'])
def searchUserByIDv1(userId):
    try:
        search = Config.getSearchService(current_app)
        result = search.searchUsersByKeyValues( dict(userId=userId) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@routes.route('/v1/users/create', methods=['POST'])
def createUserv1():
    try:
        create = Config.getCreationService(current_app)
        create.signup( request.form.to_dict(flat=True) )
        return route_utils.createJSONResponse([], 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@routes.route('/v1/users/<userId>/update', methods=['PATCH'])
def updateUserv1(userId):
    # try:
    #     userData = route_utils.getJsonFromRequest(request)
    #     userData.update({ 'userId': userId })
    #     Config.getDB(current_app).updateUser(userData)
    # except MyAppException as e:
    #     return route_utils.createJSONErrorResponse(e)
    try:
        update = Config.getUpdateService(current_app)
        userData = route_utils.getJsonFromRequest(request)
        userData.update({ 'userId': userId })
        update.updateUserByKeyValues(userData)
        return route_utils.createJSONResponse([], 200)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@routes.route('/v1/users/<userId>/delete', methods=['DELETE'])
def deleteUserv1(userId):
    try:
        Config.getDB(current_app).deleteUser([userId])
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

    return route_utils.createJSONResponse([], 200)


@routes.route('/v1/users/login', methods=['POST'])
def loginUserv1():
    try:
        userauth = Config.getUserAuth(current_app)
        authenticatedUser = userauth.login( request.form.to_dict() )
        return route_utils.createJSONResponse(
            [ route_utils.createUsersObject(authenticatedUser) ],
            200
        )
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
