# -*- coding: utf-8 -*-
"""
This file houses routes for user related api
"""

import urllib.parse

from flask import Blueprint, request, current_app, make_response

import server.app_utils as app_utils
import server.routes.route_utils  as route_utils
from server.database.filter import Filter
from server.database.paging import Paging
from server.exceptions import MyAppException

routes = Blueprint('userRoutes', __name__)

@routes.route('/v1/users', methods=['GET'])
def searchUserv1():
    # do i need this api?
    try:
        searchCriteria = route_utils.createSearchFilters(request.args, fieldName='userName')
        users = app_utils.getDB(current_app).searchUser(searchCriteria)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
    
    return route_utils.createJSONResponse([ route_utils.createUsersObject(users) ], 200)

@routes.route('/v1/users/<userId>', methods=['GET'])
def searchUserByIDv1(userId):
    try:
        searchCriteria = route_utils.createIDFilters(fieldName='userId', idValue=userId)
        users = app_utils.getDB(current_app).searchUser(searchCriteria)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

    return route_utils.createJSONResponse([ route_utils.createUsersObject(users) ], 200)

@routes.route('/v1/users/create', methods=['POST'])
def createUserv1():
    userProperties = request.form
    try:
        app_utils.getSignup(current_app).signup(userProperties)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

    return route_utils.createJSONResponse([], 200)


@routes.route('/v1/users/<userId>/update', methods=['PATCH'])
def updateUserv1(userId):
    try:
        userData = route_utils.getJsonFromRequest(request)
        userData.update({ 'userId': userId })
        app_utils.getDB(current_app).updateUser(userData)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

    return route_utils.createJSONResponse([], 200)

@routes.route('/v1/users/<userId>/delete', methods=['DELETE'])
def deleteUserv1(userId):
    try:
        app_utils.getDB(current_app).deleteUser([userId])
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

    return route_utils.createJSONResponse([], 200)