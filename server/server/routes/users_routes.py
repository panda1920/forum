# -*- coding: utf-8 -*-
"""
This file houses routes for user related API
"""
from flask import Blueprint, request, current_app, session

from server.config import Config
import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.exceptions import MyAppException

routes = Blueprint('userRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/users', methods=['GET'])
def searchUserv1():
    try:
        search = Config.getSearchService(current_app)
        result = search.searchUsersByKeyValues( request.args.to_dict(flat=True) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>', methods=['GET'])
def searchUserByIDv1(userId):
    try:
        search = Config.getSearchService(current_app)
        result = search.searchUsersByKeyValues( dict(userId=userId) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/create', methods=['POST'])
def createUserv1():
    try:
        create = Config.getCreationService(current_app)
        create.signup( route_utils.getJsonFromRequest(request) )
        return route_utils.createJSONResponse([], 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>/update', methods=['PATCH'])
def updateUserv1(userId):
    try:
        update = Config.getUpdateService(current_app)
        userData = route_utils.getJsonFromRequest(request)
        userData.update({ 'userId': userId })
        update.updateUserByKeyValues(userData)
        return route_utils.createJSONResponse([], 200)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>/delete', methods=['DELETE'])
def deleteUserByIdv1(userId):
    try:
        delete = Config.getDeleteService(current_app)
        response = delete.deleteUserByKeyValues( dict(userId=userId) )
        return route_utils.createJSONResponse([ response ], 200)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/login', methods=['POST'])
def loginUserv1():
    try:
        userauth = Config.getAuthService(current_app)
        authenticatedUser = userauth.login( route_utils.getJsonFromRequest(request) )
        return route_utils.createJSONResponse(
            [ route_utils.createUsersObject(authenticatedUser) ],
            200
        )
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/logout', methods=['POST'])
def logoutUserv1():
    try:
        userauth = Config.getAuthService(current_app)
        userauth.logout()
        return route_utils.createJSONResponse([], 200)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/session', methods=['GET'])
def getSessionUserv1():
    return route_utils.createJSONResponse([], 200)


@routes.before_request
def apply_middlewares_before():
    Config.getSessionMiddleware(current_app).setCurrentUser()


@routes.after_request
def apply_middleware_after(response):
    try:
        session_middleware = Config.getSessionMiddleware(current_app)
        updated_response = session_middleware.addCurrentUserToResponse(response)
        return updated_response
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
