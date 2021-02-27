# -*- coding: utf-8 -*-
"""
This file houses routes for user related API
"""
from flask import Blueprint, request, current_app

from server.config import Config
import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.exceptions import MyAppException
from server.entity import User

routes = Blueprint('userRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/users', methods=['GET'])
def searchUserv1():
    try:
        search = Config.getSearchService(current_app)
        result = search.searchUsersByKeyValues( request.args.to_dict(flat=True) )
        result['users'] = [ user.to_serialize() for user in result['users'] ]
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>', methods=['GET'])
def searchUserByIDv1(userId):
    try:
        search = Config.getSearchService(current_app)
        result = search.searchUsersByKeyValues( dict(userId=userId) )
        result['users'] = [ user.to_serialize() for user in result['users'] ]
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/create', methods=['POST'])
def createUserv1():
    try:
        create = Config.getCreationService(current_app)
        result = create.signup( User(route_utils.getJsonFromRequest(request)) )
        return route_utils.createResultResponse(result, 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>/update', methods=['PATCH'])
def updateUserv1(userId):
    try:
        update = Config.getUpdateService(current_app)
        user_to_update = User(route_utils.getJsonFromRequest(request))
        user_to_update.userId = userId
        result = update.updateUser(user_to_update)
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>/update-portrait', methods=['PATCH'])
def updateUserPortraitv1(userId):
    try:
        update = Config.getUpdateService(current_app)
        portrait_data = request.files['portraitImage'].read()
        user_to_update = User(dict(portraitImage=portrait_data, userId=userId))
        result = update.updateUser(user_to_update)
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>/delete', methods=['DELETE'])
def deleteUserByIdv1(userId):
    try:
        delete = Config.getDeleteService(current_app)
        result = delete.deleteUserById(userId)
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/<userId>/confirm', methods=['POST'])
def confirmUserCredentialv1(userId):
    try:
        userauth = Config.getAuthService(current_app)
        data = route_utils.getJsonFromRequest(request)
        userauth.confirm_user_credential(userId, data['password'])
        return route_utils.createResultResponse('Credentials verified')
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/login', methods=['POST'])
def loginUserv1():
    try:
        userauth = Config.getAuthService(current_app)
        authenticatedUser = userauth.login( route_utils.getJsonFromRequest(request) )
        return route_utils.createResultResponse(authenticatedUser)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/logout', methods=['POST'])
def logoutUserv1():
    try:
        userauth = Config.getAuthService(current_app)
        result = userauth.logout()
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/users/session', methods=['GET'])
def getSessionUserv1():
    return route_utils.createJSONResponse([], 200)


@routes.before_request
def apply_middlewares_before():
    Config.getRequestUserManager(current_app).setCurrentUser()


@routes.after_request
def apply_middleware_after(response):
    try:
        requestuser_manager = Config.getRequestUserManager(current_app)
        updated_response = requestuser_manager.addCurrentUserToResponse(response)
        return updated_response
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
