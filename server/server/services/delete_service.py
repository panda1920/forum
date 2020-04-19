# -*- coding: utf-8 -*-
"""
This file houses business logic related to entity deletion
"""
import logging

import server.exceptions as exceptions
from server.database.filter import PrimitiveFilter
from server.database.paging import PagingNoLimit


class DeleteService:
    """
    Class that provides methods to delete entity.
    Includes most of the business logic that is associated
    with deleting entities like users, threads etc.
    """
    def __init__(self, repo, session):
        self._repo = repo
        self._session = session

    def deleteUserByKeyValues(self, keyValues):
        """
        Delete user by passing criteria as keyValues.
        
        Args:
            keyValues(dict): criteria of user to delete
        Returns:
            result of operation
        """
        userId = keyValues.get('userId')
        if userId is None:
            logging.error('Failed to delete due to no Id specified in keyValues')
            raise exceptions.IdNotSpecifiedError('Specify entity Id to perform delete')
        self._authorizeDelete(userId)
        searchFilter = self._createSearchFilterFromKeyValuesForField(keyValues, 'userId')
        
        return self._repo.deleteUser(searchFilter)

    def deletePostByKeyValues(self, keyValues):
        """
        Delete post by passing criteria as keyValues.
        
        Args:
            keyValues(dict): criteria of post to delete
        Returns:
            result of operation
        """
        searchFilter = self._createSearchFilterFromKeyValuesForField(keyValues, 'postId')
        self._authorizeDeletePost(searchFilter)
        
        return self._repo.deletePost(searchFilter)

    def deleteThreadByKeyValues(self, keyValues):
        """
        Delete thread by passing criteria as keyValues
        
        Args:
            keyValues(dict): criteria of thread to delete
        Returns:
            result of operation
        """
        searchFilter = self._createSearchFilterFromKeyValuesForField(keyValues, 'threadId')
        self._authorizeDeleteThread(searchFilter)
        
        return self._repo.deleteThread(searchFilter)

    def _createSearchFilterFromKeyValuesForField(self, keyValues, fieldname):
        """
        Creates searchFilter used to search entities from repo,
        by extracting fieldname from keyvalues
        
        Args:
            keyValues(dict):
            fieldname(string): creates searchfilter using this fieldname
        Returns:
            PrimitiveFilter
        """
        fieldvalue = keyValues.get(fieldname, None)
        if fieldvalue is None:
            logging.error('Failed to delete due to no Id specified in keyValues')
            raise exceptions.IdNotSpecifiedError('Specify entity Id to perform delete')
        
        return PrimitiveFilter.createFilter(dict(
            operator='eq', field=fieldname, value=[ fieldvalue ]
        ))

    def _authorizeDeletePost(self, searchFilter):
        """
        Authorizes current user to delete this post.
        
        Args:
            searchFilter(PrimitiveFilter): used to search posts from repo
        Returns:
            None
        """
        posts = self._repo.searchPost(searchFilter, paging=PagingNoLimit())['posts']
        
        for post in posts:
            self._authorizeDelete( post['userId'] )

    def _authorizeDeleteThread(self, searchFilter):
        """
        Authorizes current user to delete this thread.
        
        Args:
            searchFilter(PrimitiveFilter): used to search threads from repo
        Returns:
            None
        """
        threads = self._repo.searchThread(searchFilter, paging=PagingNoLimit())['threads']
        
        for thread in threads:
            self._authorizeDelete( thread['userId'] )

    def _authorizeDelete(self, userId):
        """
        Authorizes delete operation by comparing resource owner with current user.
        Inteded to be used for cases like preventing user A from deleting posts created by user B.
        
        Args:
            userId(string): userId of resource owner
        Returns:
            None
        """
        session_user = self._session.get_user()
        if (session_user is None) or (session_user['userId'] != userId):
            logging.error('Failed operation due to unauthorized user')
            raise exceptions.UnauthorizedError('Unauthorized action')
