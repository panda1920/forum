# -*- coding: utf-8 -*-
"""
This file houses buisness logic for searches made by apis
"""

class SearchService:
    """
    Provides search service for various use cases for the upper layers.
    Coveres all entities involved in this app: user, posts, threads etc.
    Contains most of the search related business logic.
    """

    # TODO
    # user authorization
    # select fields to retrieve based on each use case
    # sanitization of args
    # possibly change return value to contain more info for the upper layer
    
    # post search can be made based on threadId, userId, createdAt, most liked...

    def __init__(self, repo, filterClass, pagingClass):
        self._repo = repo
        self._filter = filterClass
        self._paging = pagingClass

    def searchUsersByKeyValues(self, keyValues):
        searchFilters = []
        searchFilters.extend( self._createFuzzyFiltersFromSearch('userName', keyValues) )
        paging = self._paging(keyValues)
        
        if len(searchFilters) == 0:
            return dict(users=[], returnCount=0, matchedCount=0)

        return self._repo.searchUser(searchFilters, paging)

    def searchUsersById(self, userId, keyValues):
        searchFilters = []
        searchFilters.extend( self._createEqFiltersFromIds('userId', [userId]) )
        paging = self._paging(keyValues)

        return self._repo.searchUser(searchFilters, paging)

    def searchPostsByKeyValues(self, keyValues):
        searchFilters = []
        searchFilters.extend( self._createFuzzyFiltersFromSearch('content', keyValues) )
        paging = self._paging(keyValues)

        if len(searchFilters) == 0:
            return dict(posts=[], returnCount=0, matchedCount=0)

        postResult = self._repo.searchPost(searchFilters, paging)
        userSearchFilters = self._createEqFiltersFromRelatedIds(
            'userId', postResult['posts']
        )
        userResult = self._repo.searchUser(userSearchFilters)
        postsJoined = self._joinDocuments(
            postResult['posts'], userResult['users'], 'userId', 'user'
        )

        return dict(
            posts=postsJoined,
            returnCount=postResult['returnCount'],
            matchedCount=postResult['matchedCount'],
        )

    def _createFuzzyFiltersFromSearch(self, fieldname, keyValues):
        search = keyValues.get('search', None)
        if search is None:
            return []
        
        searchTerm = search.split(' ')
        searchFilter = self._filter.createFilter({
            'field': fieldname,
            'operator': 'fuzzy',
            'value': searchTerm
        })
        return [ searchFilter ]

    def _createEqFiltersFromIds(self, fieldname, ids):
        searchFilter = self._filter.createFilter({
            'field': fieldname,
            'operator': 'eq',
            'value': ids
        })
        return [ searchFilter ]

    def _createEqFiltersFromRelatedIds(self, relationFieldname, entities):
        return self._createEqFiltersFromIds(
            relationFieldname,
            [ entity[relationFieldname] for entity in entities ]
        )

    def _joinDocuments(self, primaryDocs, secondaryDocs, joinByField, secondaryName):
        joined = []
        for pdoc in primaryDocs:
            newdoc = pdoc.copy()

            for sdoc in secondaryDocs:
                if pdoc[joinByField] == sdoc[joinByField]:
                    newdoc[secondaryName] = sdoc
                    break
            joined.append(newdoc)

        return joined