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
    try:
        search = app_utils.getSearchService(current_app)
        result = search.searchUsersByKeyValues( request.args.to_dict(flat=True) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

@routes.route('/v1/users/<userId>', methods=['GET'])
def searchUserByIDv1(userId):
    try:
        search = app_utils.getSearchService(current_app)
        result = search.searchUsersByKeyValues( dict(userId=userId) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

@routes.route('/v1/users/create', methods=['POST'])
def createUserv1():
    try:
        create = app_utils.getCreationService(current_app)
        create.signup (request.form.to_dict(flat=True) )
        return route_utils.createJSONResponse([], 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

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