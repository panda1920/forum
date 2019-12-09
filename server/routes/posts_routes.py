import urllib.parse

from flask import Blueprint, request, current_app, make_response

from server.routes.routes_util import *
from server.database.filter import Filter
from server.database.paging import Paging

routes = Blueprint('postRoutes', __name__)

@routes.route('/post')
def examplepost():
    data = request.data
    print(data)
    
@routes.route('/api/post', methods=['POST'])
def postCreate():
    try:
        postData = request.form
        db = getDB()
        db.createPost({
            'userId': postData['userId'],
            'content': postData['content'],
            'postId': '111111'
        })
    except Exception as e:
        return createTextResponse(str(e), 500)

    return createTextResponse('Post was stored!', 200)

@routes.route('/api/post', methods=['GET'])
def postSearch():
    try:
        db = getDB()
        searchCriteria = urllib.parse.parse_qs( request.query_string )
        db.searchPost(searchCriteria)
        return make_response('', 200)
    except Exception as e:
        return createTextResponse(str(e), 500)
    
@routes.route('/api/post', methods=['DELETE'])
def postDelete():
    try:
        db = getDB()
        db.deletePost({
            'postId': request.form['postId']
        })
        return createTextResponse('Post was deleted!', 200)
    except Exception as e:
        return createTextResponse(str(e), 500)

@routes.route('/api/post', methods=['PATCH'])
def postUpdate():

    return createTextResponse('Post was updated!', 200)

@routes.route('/v1/posts', methods=['GET'])
def searchPostsv1():
    paging = getPaging()(request.args)
    searchFilters = createSearchFilters(request.args, 'content')
    if len(searchFilters) == 0:
        return createJSONResponse( createPostsJson([]), 400 )
    
    posts = getDB().searchPost(searchFilters, paging)

    return createJSONResponse( createPostsJson(posts), 200 )

@routes.route('/v1/posts/<postId>', methods=['GET'])
def searchPostsByIdv1(postId):
    searchFilters = createIDFilters(fieldName='postId', idValue=postId)

    try:
        posts = getDB().searchPost(searchFilters)
    except:
        return createJSONResponse( createPostsJson([]), 400)

    return createJSONResponse( createPostsJson(posts), 200)

@routes.route('/v1/posts/create', methods=['POST'])
def createPostsv1():
    try:
        newPost = request.form
        createdPost = getDB().createPost(newPost)
    except:
        return createJSONResponse( createPostsJson([]), 400)

    return createJSONResponse( createPostsJson([createdPost]), 201)

# @routes.route('/v1/posts/<postId>/update', methods=['PATCH'])
# @routes.route('/v1/posts/<postId>/delete', methods=['DELETE'])

