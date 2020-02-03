# -*- coding: utf-8 -*-
"""
This file houses utility logic used by various routes
"""

import json

from flask import make_response, current_app

import server.app_utils as app_utils
from server.database.filter import Filter
from server.exceptions import MissingQueryStringError, RequestDataTypeMismatchError

def getJsonFromRequest(req):
    jsonData = req.get_json(silent=True)
    if jsonData == None:
        raise RequestDataTypeMismatchError('Request expectind json data')
    return jsonData

def createPostsObject(posts):
    return {
        'posts': posts
    }

def createUsersObject(users):
    return {
        'users': users
    }

def createJSONErrorResponse(error, datas = [], additionalHeaders = {}):
    datas.append({
        'error': {
            'description': error.getErrorMsg()
        } 
    })
    return createJSONResponse(datas, error.getStatusCode(), additionalHeaders)

def createJSONResponse(datas, statusCode, additionalHeaders = {}):
    responseBody = {}
    for data in datas:
        responseBody.update(data)
    jsonBody = json.dumps(responseBody)

    headers = {'content-type': 'application/json'}
    headers.update(additionalHeaders)

    return make_response(jsonBody, statusCode, headers)

def createTextResponse(string, statusCode):
    return make_response(string, statusCode, {'content-type': 'text/plain'})

def createSearchFilters(requestArgs, fieldName):
    filters = []

    search = requestArgs.get('search', None)
    if not search:
        raise MissingQueryStringError('need search key and value as querystring')
    
    searchTerms = search.split(' ')
    filters.append( createFuzzySearchFilter(searchTerms, fieldName) )
    return filters

def createIDFilters(fieldName, idValue):
    filters = [
        createEQSearchFilter([idValue], fieldName)
    ]
    return filters

def createFuzzySearchFilter(searchTerms, fieldName):
    return app_utils.getFilter(current_app).createFilter({
        'field': fieldName,
        'operator': 'fuzzy',
        'value': searchTerms,
    })

def createEQSearchFilter(values, fieldName):
    return app_utils.getFilter(current_app).createFilter({
        'field': fieldName,
        'operator': 'eq',
        'value': values,
    })