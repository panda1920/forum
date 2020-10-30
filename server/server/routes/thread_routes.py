# -*- coding: utf-8 -*-
"""
This file defines routes for post related APIs
"""
from flask import Blueprint, current_app, request

import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.config import Config
from server.exceptions import MyAppException
from server.entity import Thread

routes = Blueprint('threadRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/threads', methods=['GET'])
def searchThreadsv1():
    try:
        search = Config.getSearchService(current_app)
        keyValues = request.args.to_dict(flat=True)
        result = search.searchThreadsByKeyValues(keyValues)
        result['threads'] = [ thread.to_serialize() for thread in result['threads'] ]
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/threads/<threadId>', methods=['GET'])
def searchThreadByIdv1(threadId):
    try:
        search = Config.getSearchService(current_app)
        result = search.searchThreadByExplicitId(threadId)
        result['threads'] = [ thread.to_serialize() for thread in result['threads'] ]
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/threads/create', methods=['POST'])
def createThreadv1():
    try:
        create = Config.getCreationService(current_app)
        thread_to_create = Thread(route_utils.getJsonFromRequest(request))
        result = create.createNewThread(thread_to_create)
        return route_utils.createResultResponse(result, 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/threads/<threadId>/update', methods=['PATCH'])
def updateThreadByIdv1(threadId):
    try:
        update = Config.getUpdateService(current_app)
        thread_to_update = Thread(route_utils.getJsonFromRequest(request))
        thread_to_update.threadId = threadId
        result = update.updateThread(thread_to_update)
        return route_utils.createResultResponse(result, 200)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/threads/<threadId>/delete', methods=['DELETE'])
def deleteThreadByIdv1(threadId):
    try:
        delete = Config.getDeleteService(current_app)
        result = delete.deleteThreadById(threadId)
        return route_utils.createResultResponse(result, 202)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


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
