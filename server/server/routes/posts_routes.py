# -*- coding: utf-8 -*-
"""
This file defines routes for post related API
"""

import urllib.parse

from flask import Blueprint, request, current_app, make_response

from server.config import Config
import server.routes.route_utils as route_utils
from server.routes.route_utils import cors_wrapped_route
from server.exceptions import MyAppException

routes = Blueprint('postRoutes', __name__)


@cors_wrapped_route(routes.route, '/v1/posts', methods=['GET'])
def searchPostsv1():
    try:
        search = Config.getSearchService(current_app)
        result = search.searchPostsByKeyValues( request.args.to_dict(flat=True) )
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/posts/<postId>', methods=['GET'])
def searchPostsByIdv1(postId):
    try:
        search = Config.getSearchService(current_app)
        result = search.searchPostsByKeyValues(dict(postId=postId))
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/posts/create', methods=['POST'])
def createPostsv1():
    try:
        create = Config.getCreationService(current_app)
        result = create.createNewPost( route_utils.getJsonFromRequest(request) )
        return route_utils.createResultResponse(result, 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/posts/<postId>/update', methods=['PATCH'])
def updatePostv1(postId):
    try:
        update = Config.getUpdateService(current_app)
        postUpdateProperties = { 'postId': postId }
        postUpdateProperties.update( route_utils.getJsonFromRequest(request) )
        result = update.updatePostByKeyValues(postUpdateProperties)
        return route_utils.createResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
    


@cors_wrapped_route(routes.route, '/v1/posts/<postId>/delete', methods=['DELETE'])
def deletePostByIdv1(postId):
    try:
        delete = Config.getDeleteService(current_app)
        result = delete.deletePostByKeyValues( dict(postId=postId) )
        return route_utils.createResultResponse(result)
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
