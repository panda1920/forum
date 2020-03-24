# -*- coding: utf-8 -*-
"""
This file houses business logic related to entity deletion
"""
import logging

import server.exceptions as exceptions
from server.database.filter import PrimitiveFilter
from server.database.paging import PagingNoLimit
from server.middleware.session_user import SessionUserManager


class DeleteService:
    """
    Class that provides methods to delete entity.
    Includes most of the business logic that is associated
    with deleting entities like users, threads etc.
    """
    def __init__(self, repo, context):
        self._repo = repo
        self._context = context

    def deleteUserByKeyValues(self, keyValues):
        """
        Delete user by passing criteria as keyValues.
        
        Args:
            keyValues(dict): criteria of user to delete
        Returns:
            result of operation
        """
        userId = keyValues.get('userId')
        self._authorizeDelete(userId)
        searchFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='userId', value=[ userId ]
        ))
        result = self._repo.deleteUser(searchFilter)

        return dict(result=result)

    def deletePostByKeyValues(self, keyValues):
        """
        Delete post by passing criteria as keyValues.
        
        Args:
            keyValues(dict): criteria of post to delete
        Returns:
            result of operation
        """
        postId = keyValues.get('postId')
        self._authorizeDeletePost(postId)
        searchFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='postId', value=[ postId ]
        ))
        result = self._repo.deletePost(searchFilter)

        return dict(result=result)

    def _authorizeDeletePost(self, postId):
        """
        Authorizes current user to delete this post.
        
        Args:
            postId(string): postId of post
        Returns:
            None
        """
        searchFilter = PrimitiveFilter.createFilter(dict(
            operator='eq', field='postId', value=[ postId ]
        ))
        posts = self._repo.searchPost(searchFilter, PagingNoLimit())['posts']
        
        for post in posts:
            self._authorizeDelete( post['userId'] )

    def _authorizeDelete(self, userId):
        """
        Authorizes delete operationby comparing resource owner with current user.
        Inteded to be used for cases like preventing user A from deleting posts created by user B.
        
        Args:
            userId(string): userId of resource owner
        Returns:
            None
        """
        session_user = self._context.read_global(SessionUserManager.SESSION_USER_KEY)
        if (session_user is None) or (session_user['userId'] != userId):
            logging.error('Failed operation due to unauthorized user')
            raise exceptions.UnauthorizedError('Unauthorized action')
