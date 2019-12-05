import urllib.parse

from flask import Blueprint, request, current_app, make_response

from server.routes.routes_util import getDB

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
            'post': postData['post'],
            'postId': '111111'
        })
    except Exception as e:
        return make_response(str(e), 500, {'content-type': 'text/plain'})

    return make_response('Post was stored!', 200, {'content-type': 'text/plain'})

@routes.route('/api/post', methods=['GET'])
def postSearch():
    try:
        db = getDB()
        searchCriteria = urllib.parse.parse_qs( request.query_string )
        db.searchPost(searchCriteria)
        return make_response('', 200)
    except Exception as e:
        return make_response(str(e), 500, {'content-type': 'text/plain'})
    
@routes.route('/api/post', methods=['DELETE'])
def postDelete():
    try:
        db = getDB()
        db.deletePost({
            'postId': request.form['postId']
        })
        return make_response('Post was deleted!', 200, {'content-type': 'text/plain'})
    except Exception as e:
        return make_response(str(e), 500, {'content-type': 'text/plain'})

@routes.route('/api/post', methods=['PATCH'])
def postUpdate():
    db = getDB()

    return make_response('Post was updated!', 200, {'content-type': 'text/plain'})

# @routes.route('/v1/posts', methods=['GET'])
# @routes.route('/v1/posts/create', methods=['POST'])
# @routes.route('/v1/posts/<postId>', methods=['GET'])
# @routes.route('/v1/posts/<postId>/update', methods=['PATCH'])
# @routes.route('/v1/posts/<postId>/delete', methods=['DELETE'])