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


@cors_wrapped_route(routes.route, '/post')
def examplepost():
    data = request.data
    print(data)
    

@cors_wrapped_route(routes.route, '/api/post', methods=['POST'])
def postCreate():
    try:
        postData = request.form
        db = Config.getDB(current_app)
        db.createPost({
            'userId': postData['userId'],
            'content': postData['content'],
            'postId': '111111'
        })
    except Exception as e:
        return route_utils.createTextResponse(str(e), 500)

    return route_utils.createTextResponse('Post was stored!', 200)


@cors_wrapped_route(routes.route, '/api/post', methods=['GET'])
def postSearch():
    try:
        db = Config.getDB(current_app)
        searchCriteria = urllib.parse.parse_qs( request.query_string )
        db.searchPost(searchCriteria)
        return make_response('', 200)
    except Exception as e:
        return route_utils.createTextResponse(str(e), 500)
    pass
    

@cors_wrapped_route(routes.route, '/api/post', methods=['DELETE'])
def postDelete():
    try:
        db = Config.getDB(current_app)
        db.deletePost({
            'postId': request.form['postId']
        })
        return route_utils.createTextResponse('Post was deleted!', 200)
    except Exception as e:
        return route_utils.createTextResponse(str(e), 500)


@cors_wrapped_route(routes.route, '/api/post', methods=['PATCH'])
def postUpdate():

    return route_utils.createTextResponse('Post was updated!', 200)


@cors_wrapped_route(routes.route, '/v1/posts', methods=['GET'])
def searchPostsv1():
    try:
        search = Config.getSearchService(current_app)
        result = search.searchPostsByKeyValues( request.args.to_dict(flat=True) )
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/posts/<postId>', methods=['GET'])
def searchPostsByIdv1(postId):
    try:
        search = Config.getSearchService(current_app)
        result = search.searchPostsByKeyValues(dict(postId=postId))
        return route_utils.createSearchResultResponse(result)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/posts/create', methods=['POST'])
def createPostsv1():
    try:
        create = Config.getCreationService(current_app)
        # js = route_utils.getJsonFromRequest(request)
        # pdb.set_trace()
        create.createNewPost( route_utils.getJsonFromRequest(request) )
        return route_utils.createJSONResponse([], 201)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)


@cors_wrapped_route(routes.route, '/v1/posts/<postId>/update', methods=['PATCH'])
def updatePostv1(postId):
    try:
        update = Config.getUpdateService(current_app)
        postUpdateProperties = { 'postId': postId }
        postUpdateProperties.update( route_utils.getJsonFromRequest(request) )
        update.updatePostByKeyValues(postUpdateProperties)
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)
    
    return route_utils.createJSONResponse([], 200)


@cors_wrapped_route(routes.route, '/v1/posts/<postId>/delete', methods=['DELETE'])
def deletePostv1(postId):
    try:
        Config.getDB(current_app).deletePost([postId])
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e)

    return route_utils.createTextResponse('delete successful!', 200)


@routes.before_request
def apply_middlewares_before():
    Config.getSessionUser(current_app).setCurrentUser()


@routes.after_request
def apply_middleware_after(response):
    Config.getSessionUser(current_app).addCurrentUserToResponse(response)
    return response
