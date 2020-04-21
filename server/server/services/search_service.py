# -*- coding: utf-8 -*-
"""
This file houses business logic for searches made by apis
"""
from server.database.sorter import AscendingSorter, DescendingSorter, NullSorter
import server.entity.user as user
import server.entity.post as post
import server.entity.thread as thread


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
        boardId='eq',
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
        searchFilter = self._createFiltersForDesignatedFields(
            keyValues, 'userName', 'displayName'
        )
        if searchFilter is None:
            return dict(users=[], returnCount=0, matchedCount=0)
        paging = self._paging(keyValues)
        sorter = self._createSorterFromKeyValues(keyValues)
        
        result = self._repo.searchUser(searchFilter, paging=paging, sorter=sorter)

        return dict(
            users=self._removeUserPrivateData( result['users'] ),
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def searchPostsByKeyValues(self, keyValues):
        searchFilter = self._createFiltersForDesignatedFields(
            keyValues, 'content'
        )
        if searchFilter is None:
            return dict(posts=[], returnCount=0, matchedCount=0)
        paging = self._paging(keyValues)
        sorter = self._createSorterFromKeyValues(keyValues)
        
        result = self._repo.searchPost(searchFilter, paging=paging, sorter=sorter)
        posts = self._removePostPrivateData( result['posts'] )
        postsJoined = self._joinOwner(posts)

        return dict(
            posts=postsJoined,
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def searchThreadsByKeyValues(self, keyValues):
        """
        Searches for threads based on criterias in keyValues
        
        Args:
            keyValues(dict): critieras to search
        Returns:
            dict: result of search operation
        """
        searchFilter = self._createFiltersForDesignatedFields(
            keyValues, 'subject', 'title'
        )
        if searchFilter is None:
            return dict(threads=[], returnCount=0, matchedCount=0)
        paging = self._paging(keyValues)
        sorter = self._createSorterFromKeyValues(keyValues)

        result = self._repo.searchThread(searchFilter, paging=paging, sorter=sorter)
        threads = self._removeThreadPrivateData( result['threads'] )
        threads = self._joinOwner(threads)
        threadsJoined = self._joinLastPost(threads)
        
        return dict(
            threads=threadsJoined,
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def searchThreadByExplicitId(self, threadId):
        """
        Searches for thread based on threadId
        
        Args:
            threadId(string): Id of thread to search
        Returns:
            dict: result of search operation
        """
        searchFilter = self._createFiltersForDesignatedFields(dict(threadId=threadId))
        if searchFilter is None:
            return dict(threads=[], returnCount=0, matchedCount=0)
        paging = self._paging()

        result = self._repo.searchThread(searchFilter, paging=paging)
        threads = self._removeThreadPrivateData( result['threads'] )
        threadsJoined = self._joinOwner(threads)

        self._repo.updateThread(searchFilter, dict(increment='views'))

        return dict(
            threads=threadsJoined,
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def _createFiltersForDesignatedFields(self, keyValues, *fieldnames):
        searchFilters = self._createFuzzyFilterFromSearch(keyValues, fieldnames)
        predetermined = self._createFiltersForPredeterminedFields(keyValues)

        if len(searchFilters) == 0 and len(predetermined) == 0:
            return None

        # if there is no search,
        # or-aggregate would always return false,
        # which in turn makes and-aggregate evaluate to false automatically.
        # To avoid this happpening, we must not add searches to and-aggregate for such case
        if len(searchFilters) == 0:
            filtersToAggregate = predetermined
        else:
            searches = self._aggregate.createFilter('or', searchFilters)
            filtersToAggregate = [ *predetermined, searches ]
        return self._aggregate.createFilter('and', filtersToAggregate)

    def _createFuzzyFilterFromSearch(self, keyValues, fieldnames):
        searchFilters = []
        for fieldname in fieldnames:
            search = keyValues.get('search', None)
            if search is None:
                continue
        
            searchTerm = search.split(' ')
            searchFilters.append( self._createFilter(fieldname, 'fuzzy', searchTerm) )

        return searchFilters

    def _createFilter(self, fieldname, operator, values):
        return self._filter.createFilter(dict(
            field=fieldname,
            operator=operator,
            value=values
        ))

    def _createFiltersForPredeterminedFields(self, keyValues):
        searchFilters = []
        for fieldname, opstring in self.SEARCHKEY_TO_FILTER_OPSTRING_MAPPING.items():
            value = keyValues.get(fieldname, None)
            if value is None:
                continue

            f = self._createFilter(fieldname, opstring, [ value ])
            searchFilters.append(f)

        return searchFilters

    def _joinOwner(self, entities):
        """
        add owner user information to each entity document
        by searching for it in repo
        
        Args:
            entities(list): documents of entities like posts
        Returns:
            list of documents
        """
        userSearchFilter = self._createEqFiltersFromRelatedIds('userId', 'userId', entities)
        users = self._repo.searchUser(userSearchFilter)['users']
        users = self._removeUserPrivateData(users)

        return self._joinDocuments(entities, users, 'userId', 'userId', 'owner')

    def _joinLastPost(self, entities):
        """
        add last post information to each entity document
        by searching for it in repo
        
        Args:
            entities(list): documents of entities like threads
        Returns:
            list of documents
        """
        postSearchFilter = self._createEqFiltersFromRelatedIds('postId', 'lastPostId', entities)
        result = self._repo.searchPost(postSearchFilter)
        posts = self._removePostPrivateData( result['posts'] )
        posts = self._joinOwner(posts)

        return self._joinDocuments(entities, posts, 'lastPostId', 'postId', 'lastPost')

    def _createEqFiltersFromRelatedIds(self, filterFieldname, entityFieldname, entities):
        return self._createFilter(
            filterFieldname, 'eq',
            [ entity[entityFieldname] for entity in entities ]
        )

    def _joinDocuments(
        self, primaryDocs, secondaryDocs, primaryField, secondaryField, newRelationName
    ):
        """
        Join two sets of documents by specified fieldnames.
        When specified field value matches, secondary document is inserted into primary.
        
        Args:
            primaryDocs(list): inject secondary document to this if possible
            secondaryDocs(list): documents to inject
            primaryField(string): fieldname in primary to relate
            secondaryField(string): fieldname in secondary to relate
            newRelationName(string): new fieldname created in primary to put secondary under
        Returns:
            list of documents
        """
        joined = []
        for pdoc in primaryDocs:
            newdoc = pdoc.copy()

            for sdoc in secondaryDocs:
                if pdoc[primaryField] == sdoc[secondaryField]:
                    newdoc[newRelationName] = sdoc
                    break
            joined.append(newdoc)

        return joined

    def _removeUserPrivateData(self, users):
        """
        Remove private fields from users
        
        Args:
            users(dict): list of users
        Returns:
            list of users that are filtered of private fields
        """
        return [ user.removePrivateInfo(u) for u in users ]

    def _removePostPrivateData(self, posts):
        """
        Remove private fields from posts
        
        Args:
            posts(dict): list of posts
        Returns:
            list of posts that are filtered of private fields
        """
        return [ post.removePrivateInfo(u) for u in posts ]

    def _removeThreadPrivateData(self, threads):
        """
        Remove private fields from threads
        
        Args:
            threads(dict): list of threads
        Returns:
            list of threads that are filtered of private fields
        """
        return [ thread.removePrivateInfo(u) for u in threads ]

    def _createSorterFromKeyValues(self, keyValues):
        """
        Constructs appropriate Sorter class from keyValues
        Produces NullSorter if no 'sortBy' field was found'

        Args:
            keyValues(dict)
        Returns:
            Sorter class
        """
        sortField = keyValues.get('sortBy', None)
        if sortField is None:
            return NullSorter()

        order = keyValues.get('order', None)
        if order == 'desc':
            return DescendingSorter(sortField)
        else:
            return AscendingSorter(sortField)
