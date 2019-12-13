import json

from flask import current_app, make_response

from server.database.filter import Filter
from server.exceptions import MissingQueryStringError, RequestDataTypeMismatchError

def getDB():
    return current_app.config['DATABASE_OBJECT']

def getFilter():
    return current_app.config['SEARCH_FILTER']

def getPaging():
    return current_app.config['PAGING']

def getJsonFromRequest(req):
    jsonData = req.get_json(silent=True)
    if jsonData == None:
        raise RequestDataTypeMismatchError('Request expectind json data')
    return jsonData

def createPostsObject(posts):
    return {
        'posts': posts
    }

def createJSONErrorResponse(error, infos = [], additionalHeaders = {}):
    infos.append({
        'error': {
            'description': error.getErrorMsg()
        } 
    })
    return createJSONResponse(infos, error.getStatusCode(), additionalHeaders)

def createJSONResponse(infos, statusCode, additionalHeaders = {}):
    responseBody = {}
    for info in infos:
        responseBody.update(info)
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
    
    searchTerms = searchTerms = search.split(' ')
    filters.append( createFuzzySearchFilter(searchTerms, fieldName) )
    return filters

def createIDFilters(fieldName, idValue):
    filters = [
        createEQSearchFilter([idValue], fieldName)
    ]
    return filters

def createFuzzySearchFilter(searchTerms, fieldName):
    return getFilter().createFilter({
        'field': fieldName,
        'operator': 'fuzzy',
        'value': searchTerms,
    })

def createEQSearchFilter(values, fieldName):
    return getFilter().createFilter({
        'field': fieldName,
        'operator': 'eq',
        'value': values,
    })