# -*- coding: utf-8 -*-
"""
This file houses utility logic used by various routes
"""

import json
import os

from flask import make_response, request, current_app

from server.exceptions import RequestDataTypeMismatchError


def getJsonFromRequest(req):
    jsonData = req.get_json(silent=True)
    if jsonData is None:
        raise RequestDataTypeMismatchError('Request expecting json data')
    return jsonData


def createPostsObject(posts):
    return {
        'posts': posts
    }


def createUsersObject(*users):
    return {
        'users': users
    }


def createResultResponse(result, status_code=200):
    return createJSONResponse([ dict(result=result) ], status_code)


def createJSONErrorResponse(error, datas=[], additionalHeaders={}):
    datas.append({
        'error': {
            'description': error.getErrorMsg()
        }
    })
    
    return createJSONResponse(datas, error.getStatusCode(), additionalHeaders)


def createJSONResponse(datas, statusCode, additionalHeaders={}):
    responseBody = {}
    for data in datas:
        responseBody.update(data)
    jsonBody = json.dumps(responseBody)

    headers = {'Content-Type': 'application/json'}
    headers.update(additionalHeaders)

    return createCorsifiedResponse(jsonBody, statusCode, headers)


def createTextResponse(string, statusCode):
    return createCorsifiedResponse(string, statusCode, {'Content-Type': 'text/plain'})


def createCorsifiedResponse(string, statusCode, headers):
    cors_headers = { 'Access-Control-Allow-Origin': os.getenv('CORS_ALLOWED_ORIGINS', '*') }
    cors_headers.update(headers)
    return make_response(string, statusCode, cors_headers)


def cors_wrapped_route(route_func, path, **options):
    """
    wraps app.route, blueprint.route
    so it returns CORS preflight response for any OPTIONS request
    
    Args:
        route_func(func): designate Blueprint.route or app.route
        path(string): url
    Returns:
        response object
    """
    def inner(func):
        def wrapper(*args, **kwargs):
            if request.method == 'OPTIONS':
                return preflight_response()
            elif is_valid_request():
                return func(*args, **kwargs)
            else:
                return createJSONResponse(
                    [{ 'error': { 'description': 'Invalid Request' } }], 400
                )

        wrapper.__name__ = func.__name__

        # make sure OPTIONS method are allowed in routes
        # so CORS preflight can be handled by the wrapper function above
        if 'methods' in options:
            if 'OPTIONS' not in options['methods']:
                options['methods'].append('OPTIONS')

        return route_func(path, **options)(wrapper)

    return inner


def preflight_response():
    response = make_response()
    cors_headers = {
        'Access-Control-Allow-Origin': os.getenv('CORS_ALLOWED_ORIGINS', '*'),
        'Access-Control-Allow-Headers': os.getenv('CORS_ALLOWED_HEADERS', '*'),
        'Access-Control-Allow-Methods': os.getenv('CORS_ALLOWED_METHODS', '*'),
    }
    response.headers.extend(cors_headers)
    response.status_code = 204

    return response


def is_valid_request():
    """
    Check against CSRF.
    Make sure request contains a custom header,
    and that its origin is allowed.
    
    Args:
        None
    Returns:
        Boolean
    """
    # disable checks during tests
    if current_app.testing:
        return True

    headers = request.headers
    custom_header = 'X-Requested-With'
    origin = headers.get('Origin', None)

    # check custom header
    if custom_header not in headers:
        return False
    
    # if CORS request, origin must be allowed
    if origin is not None:
        allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '*')
        if allowed_origins != '*' and origin not in allowed_origins.split(', '):
            return False

    return True
