import json

from flask import current_app, make_response

from server.database.filter import Filter

def getDB():
    return current_app.config['DATABASE_OBJECT']

def getFilter():
    return current_app.config['SEARCH_FILTER']

def getPaging():
    return current_app.config['PAGING']

def createPostsJson(posts):
    return json.dumps({ 'posts': posts })

def createJSONResponse(json, statusCode):
    return make_response(json, statusCode, {'content-type': 'application/json'})

def createTextResponse(string, statusCode):
    return make_response(string, statusCode, {'content-type': 'text/plain'})

def createSearchFilters(requestArgs, fieldName):
    filters = []

    search = requestArgs.get('search', None)
    if search:
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