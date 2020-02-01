import urllib.parse

from flask import Blueprint, request, current_app, make_response

import server.app_utils as app_utils
import server.routes.route_utils  as route_utils 
from server.database.filter import Filter
from server.database.paging import Paging
from server.exceptions import MyAppException

routes = Blueprint('postRoutes', __name__)

@routes.route('/post')
def examplepost():
    data = request.data
    print(data)
    
@routes.route('/api/post', methods=['POST'])
def postCreate():
    try:
        postData = request.form
        db = app_utils.getDB(current_app)
        db.createPost({
            'userId': postData['userId'],
            'content': postData['content'],
            'postId': '111111'
        })
    except Exception as e:
        return route_utils .createTextResponse(str(e), 500)

    return route_utils .createTextResponse('Post was stored!', 200)

@routes.route('/api/post', methods=['GET'])
def postSearch():
    try:
        db = app_utils.getDB(current_app)
        searchCriteria = urllib.parse.parse_qs( request.query_string )
        db.searchPost(searchCriteria)
        return make_response('', 200)
    except Exception as e:
        return route_utils .createTextResponse(str(e), 500)
    
@routes.route('/api/post', methods=['DELETE'])
def postDelete():
    try:
        db = app_utils.getDB(current_app)
        db.deletePost({
            'postId': request.form['postId']
        })
        return route_utils .createTextResponse('Post was deleted!', 200)
    except Exception as e:
        return route_utils .createTextResponse(str(e), 500)

@routes.route('/api/post', methods=['PATCH'])
def postUpdate():

    return route_utils .createTextResponse('Post was updated!', 200)

@routes.route('/v1/posts', methods=['GET'])
def searchPostsv1():
    try:
        paging = app_utils.getPaging(current_app)(request.args)
        searchFilters = route_utils .createSearchFilters(request.args, 'content')
        posts = app_utils.getDB(current_app).searchPost(searchFilters, paging)
    except MyAppException as e:
        return route_utils .createJSONErrorResponse(e, [ route_utils .createPostsObject([]) ])

    return route_utils .createJSONResponse([ route_utils .createPostsObject(posts) ], 200)

@routes.route('/v1/posts/<postId>', methods=['GET'])
def searchPostsByIdv1(postId):
    searchFilters = route_utils.createIDFilters(fieldName='postId', idValue=postId)

    try:
        posts = app_utils.getDB(current_app).searchPost(searchFilters)
    except MyAppException as e:
        return route_utils .createJSONErrorResponse(e, [ route_utils .createPostsObject([]) ])

    return route_utils .createJSONResponse([ route_utils .createPostsObject(posts) ], 200)

@routes.route('/v1/posts/create', methods=['POST'])
def createPostsv1():
    try:
        postProps = request.form
        app_utils.getDB(current_app).createPost({**postProps})
    except MyAppException as e:
        return route_utils.createJSONErrorResponse(e, [ route_utils .createPostsObject([]) ])
    except Exception as e:
        print(e)
        raise e

    return route_utils.createJSONResponse([ route_utils .createPostsObject([]) ], 201)


@routes.route('/v1/posts/<postId>/update', methods=['PATCH'])
def updatePostv1(postId):
    try:
        postUpdateProperties = { 'postId': postId }
        postUpdateProperties.update( route_utils .getJsonFromRequest(request) )
        app_utils.getDB(current_app).updatePost(postUpdateProperties)
    except MyAppException as e:
        return route_utils .createJSONErrorResponse(e)
    
    return route_utils .createJSONResponse([], 200)

@routes.route('/v1/posts/<postId>/delete', methods=['DELETE'])
def deletePostv1(postId):
    try:
        app_utils.getDB(current_app).deletePost([postId])
    except MyAppException as e:
        return route_utils .createJSONErrorResponse(e)

    return route_utils .createTextResponse('delete successful!', 200)

# error resposne
# pass e
# want to list the content to be included
# optinally pass headers


