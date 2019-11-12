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
def post():
    data = request.data
    db = current_app.config['DATABASE_OBJECT']
    
    try:
        db.createPost(data)
    except:
        return make_response('Failed to store post!', 500, {'content-type': 'text/plain'})

    return make_response('Post was stored!', 200, {'content-type': 'text/plain'})