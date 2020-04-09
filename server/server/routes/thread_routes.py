# -*- coding: utf-8 -*-
"""
This file defines routes for post related APIs
"""
from flask import Blueprint, current_app, request

import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.config import Config
from server.exceptions import MyAppException

routes = Blueprint('threadRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/thread', methods=['POST'])
def searchThreadsv1():
    try:
        search = Config.getSearchService(current_app)
        keyValues = route_utils.getJsonFromRequest(request)
        result = search.searchThreadsByKeyValues(keyValues)
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/thread/<threadId>', methods=['POST'])
def searchThreadByIdv1(threadId):
    try:
        search = Config.getSearchService(current_app)
        keyValues = route_utils.getJsonFromRequest(request)
        keyValues.update({ 'threadId': threadId })
        result = search.searchThreadsByKeyValues(keyValues)
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/thread/create', methods=['POST'])
def createThreadv1():
    try:
        create = Config.getCreationService(current_app)
        keyValues = route_utils.getJsonFromRequest(request)
        result = create.createNewThread(keyValues)
        return route_utils.createResultResponse(result, 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/thread/<threadId>/update', methods=['PATCH'])
def updateThreadByIdv1(threadId):
    try:
        update = Config.getUpdateService(current_app)
        keyValues = route_utils.getJsonFromRequest(request)
        keyValues.update({ 'threadId': threadId })
        result = update.updateThreadByKeyValues(keyValues)
        return route_utils.createResultResponse(result, 200)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/thread/<threadId>/delete', methods=['DELETE'])
def deleteThreadByIdv1(threadId):
    try:
        delete = Config.getDeleteService(current_app)
        keyValues = { 'threadId': threadId }
        result = delete.deleteThreadByKeyValues(keyValues)
        return route_utils.createResultResponse(result, 202)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


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
