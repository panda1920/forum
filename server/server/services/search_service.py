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

    SEARCHKEY_TO_FILTER_OPSTRING_MAPPING = dict(
        userId='eq',
        postId='eq',
        threadId='eq',
        createdAt='eq',
    )

    # TODO
    # user authorization
    # select fields to retrieve based on each use case
    # sanitization of args
    # possibly change return value to contain more info for the upper layer
    
    # post search can be made based on threadId, userId, createdAt...

    def __init__(self, repo, filterClass, aggregateFilterClass, pagingClass):
        self._repo = repo
        self._filter = filterClass
        self._aggregate = aggregateFilterClass
        self._paging = pagingClass

    def searchUsersByKeyValues(self, keyValues):
        searchFilters = self._createFiltersForDesignatedFields(
            keyValues, 'userName', 'displayName'
        )
        if len(searchFilters) == 0:
            return dict(users=[], returnCount=0, matchedCount=0)
        aggregate = self._aggregate.createFilter('or', searchFilters)
        paging = self._paging(keyValues)

        result = self._repo.searchUser(aggregate, paging)

        return dict(
            users=self._makeSerializable( result['users'] ),
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def searchPostsByKeyValues(self, keyValues):
        # create aggregate search filter
        searchFilters = []
        searchFilters.extend( self._createFiltersForDesignatedFields(
            keyValues, 'content'
        ) )
        searchFilters.extend( self._createFiltersForPredeterminedFields(keyValues) )
        if len(searchFilters) == 0:
            return dict(posts=[], returnCount=0, matchedCount=0)
        
        aggregate = self._aggregate.createFilter('and', searchFilters)
        paging = self._paging(keyValues)
        
        postResult = self._repo.searchPost(aggregate, paging)
        
        posts = self._makeSerializable( postResult['posts'] )
        userSearchFilter = self._createEqFiltersFromRelatedIds('userId', posts)
        users = self._makeSerializable( self._repo.searchUser(userSearchFilter)['users'] )
        postsJoined = self._joinDocuments(posts, users, 'userId', 'user')

        return dict(
            posts=postsJoined,
            returnCount=postResult['returnCount'],
            matchedCount=postResult['matchedCount'],
        )

    def _createFiltersForDesignatedFields(self, keyValues, *fieldnames):
        searchFilters = [
            self._createFuzzyFilterFromSearch(keyValues, fieldname)
            for fieldname in fieldnames
        ]
        searchFilters = [ f for f in searchFilters if f is not None ]

        return searchFilters

    def _createFuzzyFilterFromSearch(self, keyValues, fieldname):
        search = keyValues.get('search', None)
        if search is None:
            return None
        
        searchTerm = search.split(' ')
        searchFilter = self._createFilter(fieldname, 'fuzzy', searchTerm)
        return searchFilter

    def _createFilter(self, fieldname, operator, values):
        return self._filter.createFilter(dict(
            field=fieldname,
            operator=operator,
            value=values
        ))

    def _createFiltersForPredeterminedFields(self, keyValues):
        searchFilters = []
        for fieldname, opstring in self.SEARCHKEY_TO_FILTER_OPSTRING_MAPPING.items():
            if fieldname in keyValues:
                searchFilters.append(self._createFilter(
                    fieldname, opstring, [ keyValues[fieldname] ]
                ))

        return searchFilters

    def _createEqFiltersFromRelatedIds(self, relationFieldname, entities):
        return self._createFilter(
            relationFieldname, 'eq',
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

    def _makeSerializable(self, entities):
        """
        remove fields that may not be serializable
        
        Args:
            entities(list of dict): list of entities
        Returns:
            list that is serializable
        """
        for entity in entities:
            entity.pop('_id', None)
        return entities
