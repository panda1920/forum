import time
import urllib.parse
from flask import Blueprint, render_template, request, current_app, make_response


routes = Blueprint('routes', __name__,)

@routes.route('/')
@routes.route('/index')
def hello_world():
    return 'hello world!'

@routes.route('/jsonstring')
def jsonstring():
    json = r'{ "name": "Danny", "age": "13", "families": ["mother", "father", "sister"]}'
    return json

@routes.route('/template')
def template():
    return render_template('hello.html', user='default')
@routes.route('/template/<username>')
def template1(username):
    return render_template('hello.html', user=username)

@routes.route('/post')
def examplepost():
    data = request.data
    print(data)
    
@routes.route('/api/post', methods=['POST'])
def postCreate():
    try:
        postData = request.form
        db = current_app.config['DATABASE_OBJECT']
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
        db = current_app.config['DATABASE_OBJECT']
        searchCriteria = urllib.parse.parse_qs( request.query_string )
        db.searchPost(searchCriteria)
        return make_response('', 200)
    except Exception as e:
        return make_response(str(e), 500, {'content-type': 'text/plain'})
    
@routes.route('/api/post', methods=['DELETE'])
def postDelete():
    try:
        db = current_app.config['DATABASE_OBJECT']
        db.deletePost({
            'postId': request.form['postId']
        })
        return make_response('Post was deleted!', 200, {'content-type': 'text/plain'})
    except Exception as e:
        return make_response(str(e), 500, {'content-type': 'text/plain'})

@routes.route('/api/post', methods=['PATCH'])
def postUpdate():
    db = current_app.config['DATABASE_OBJECT']

    return make_response('Post was updated!', 200, {'content-type': 'text/plain'})