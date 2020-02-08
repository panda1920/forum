# -*- coding: utf-8 -*-
"""
Utility functions for the entire app
"""

def getDB(app):
    return app.config['DATABASE_REPOSITORY']

def getFilter(app):
    return app.config['SEARCH_FILTER']

def getAggregateFilter(app):
    return app.config['AGGREGATE_FILTER']

def getPaging(app):
    return app.config['PAGING']

def getuserAuth(app):
    return app.config['USER_AUTHENTICATION']

def getSignup(app):
    return app.config['SIGNUP']

def getSearchService(app):
    return app.config['SEARCH_SERVICE']

def getCreationService(app):
    return app.config['CREATION_SERVICE']