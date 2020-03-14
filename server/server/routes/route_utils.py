# -*- coding: utf-8 -*-
"""
This file houses utility logic used by various routes
"""

import json

from flask import make_response, request

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


def createSearchResultObject(result):
    return dict(
        searchResult=result
    )


def createSearchResultResponse(result):
    return createJSONResponse([ dict(searchResult=result) ], 200)


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
    cors_headers = { 'Access-Control-Allow-Origin': '*' }
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
                return createPreflightCorsResponse()
            else:
                return func(*args, **kwargs)

        wrapper.__name__ = func.__name__

        # make sure OPTIONS method are allowed in routes
        # so CORS preflight can be handled by the wrapper function above
        if 'methods' in options:
            if 'OPTIONS' not in options['methods']:
                options['methods'].append('OPTIONS')

        return route_func(path, **options)(wrapper)

    return inner


def createPreflightCorsResponse():
    response = make_response()
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*',
    }
    response.headers.extend(cors_headers)

    return response
