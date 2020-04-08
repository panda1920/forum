# -*- coding: utf-8 -*-
"""
This file defines routes for post related APIs
"""
from flask import Blueprint, current_app

import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.config import Config
from server.exceptions import MyAppException

routes = Blueprint('threadRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/thread', methods=['POST'])
def searchThreadsv1():
    return route_utils.createJSONResponse([], 200)


@cors_wrapped_route(routes.route, '/v1/thread/<threadId>', methods=['POST'])
def searchThreadByIdv1(threadId):
    return route_utils.createJSONResponse([], 200)


@cors_wrapped_route(routes.route, '/v1/thread/create', methods=['POST'])
def createThreadv1():
    return route_utils.createJSONResponse([], 201)


@cors_wrapped_route(routes.route, '/v1/thread/update/<threadId>', methods=['PATCH'])
def updateThreadByIdv1(threadId):
    return route_utils.createJSONResponse([], 200)


@cors_wrapped_route(routes.route, '/v1/thread/delete/<threadId>', methods=['DELETE'])
def deleteThreadByIdv1(threadId):
    return route_utils.createJSONResponse([], 202)


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
