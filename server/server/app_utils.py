# -*- coding: utf-8 -*-
"""
Utility class for the entire app
"""

def getDB(app):
    return app.config['DATABASE_OBJECT']

def getFilter(app):
    return app.config['SEARCH_FILTER']

def getPaging(app):
    return app.config['PAGING']

def getuserAuth(app):
    return app.config['USER_AUTHENTICATION']

def getSignup(app):
    return app.config['SIGNUP']

def getSearchService(app):
    return app.config['SEARCH_SERVICE']