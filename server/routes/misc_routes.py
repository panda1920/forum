from flask import Blueprint, request, current_app, render_template

routes = Blueprint('miscRoutes', __name__)

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