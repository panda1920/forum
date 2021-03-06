# -*- coding: utf-8 -*-
"""
This file houses business logic for searches made by apis
"""
from server.database.sorter import AscendingSorter, DescendingSorter, NullSorter
from server.entity import Thread


class SearchService:
    """
    Provides methods to search for entities.
    Contains most of the search related business logic.
    """

    # TODO
    # sanitization of args

    def __init__(self, repo, searchFilterCreator, filterClass, aggregateFilterClass, pagingClass):
        self._repo = repo
        self._searchFilterCreator = searchFilterCreator
        self._filter = filterClass
        self._aggregate = aggregateFilterClass
        self._paging = pagingClass

    def searchUsersByKeyValues(self, keyValues):
        searchFilter = self._searchFilterCreator.create_usersearch(keyValues)
        paging = self._paging(keyValues)
        sorter = self._createSorterFromKeyValues(keyValues)
        
        result = self._repo.searchUser(searchFilter, paging=paging, sorter=sorter)

        return dict(
            users=result['users'],
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def searchPostsByKeyValues(self, keyValues):
        searchFilter = self._searchFilterCreator.create_postsearch(keyValues)
        paging = self._paging(keyValues)
        sorter = self._createSorterFromKeyValues(keyValues)
        
        result = self._repo.searchPost(searchFilter, paging=paging, sorter=sorter)
        self._joinOwner(result['posts'])

        return dict(
            posts=result['posts'],
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def searchThreadsByKeyValues(self, keyValues):
        """
        Searches for threads based on criterias in keyValues
        
        Args:
            keyValues(dict): criterias to search
        Returns:
            dict: result of search operation
        """
        searchFilter = self._searchFilterCreator.create_threadsearch(keyValues)
        paging = self._paging(keyValues)
        sorter = self._createSorterFromKeyValues(keyValues)

        result = self._repo.searchThread(searchFilter, paging=paging, sorter=sorter)
        self._joinOwner(result['threads'])
        self._joinLastPost(result['threads'])
        
        return dict(
            threads=result['threads'],
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
        searchFilter = self._searchFilterCreator.create_threadsearch(
            dict(threadId=threadId)
        )
        paging = self._paging()

        result = self._repo.searchThread(searchFilter, paging=paging)
        self._joinOwner(result['threads'])

        updateThread = Thread()
        updateThread.increment = 'views'
        self._repo.updateThread(searchFilter, updateThread)

        return dict(
            threads=result['threads'],
            returnCount=result['returnCount'],
            matchedCount=result['matchedCount'],
        )

    def _createFilter(self, fieldname, operator, values):
        return self._filter.createFilter(dict(
            field=fieldname,
            operator=operator,
            value=values
        ))

    def _joinOwner(self, entities):
        """
        add owner user information to each entity document
        by searching for it in repo
        
        Args:
            entities(list): documents of entities like posts
        Returns:
            None
        """
        if len(entities) == 0:
            return

        userSearchFilter = self._createEqFiltersFromRelatedFieldnames('userId', 'userId', entities)
        users = self._repo.searchUser(userSearchFilter)['users']
        self._joinDocuments(entities, users, 'userId', 'userId', 'owner')

    def _joinLastPost(self, entities):
        """
        add last post information to each entity document
        by searching for it in repo
        
        Args:
            entities(list): documents of entities like threads
        Returns:
            None
        """
        if len(entities) == 0:
            return 0

        postSearchFilter = self._createEqFiltersFromRelatedFieldnames('postId', 'lastPostId', entities)
        posts = self._repo.searchPost(postSearchFilter)['posts']
        self._joinOwner(posts)
        self._joinDocuments(entities, posts, 'lastPostId', 'postId', 'lastPost')

    def _createEqFiltersFromRelatedFieldnames(self, filterFieldname, entityFieldname, entities):
        value = [
            getattr(entity, entityFieldname)
            for entity in entities
            if getattr(entity, entityFieldname, None) is not None
        ]

        return self._createFilter(filterFieldname, 'eq', value)

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
            None
        """
        for pdoc in primaryDocs:
            p_fieldvalue = getattr(pdoc, primaryField)
            p_relation = getattr(pdoc, newRelationName, [])

            for sdoc in secondaryDocs:
                s_fieldvalue = getattr(sdoc, secondaryField)
                if not p_fieldvalue == s_fieldvalue:
                    continue

                p_relation.append(sdoc)

            setattr(pdoc, newRelationName, p_relation)

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
