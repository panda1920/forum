# -*- coding: utf-8 -*-
"""
This file houses business logic related to entity update
"""

import logging

import server.exceptions as exceptions
from server.services.session import SessionService


class UpdateService:
    """
    Class that provides methods to update entities.
    Includes most of the business logic related to update operations.
    """
    def __init__(self, repo, PrimitiveFilter, session):
        self._repo = repo
        self._filter = PrimitiveFilter
        self._session = session

    def updateUserByKeyValues(self, keyValues):
        searchFilter = self._createEQSearchFilter(keyValues, 'userId')
        self._authorizeUpdateUser(searchFilter)
        update = keyValues.copy()
        update.pop('userId')

        return self._repo.updateUser(searchFilter, update)

    def updatePostByKeyValues(self, keyValues):
        searchFilter = self._createEQSearchFilter(keyValues, 'postId')
        self._authorizeUpdatePost(searchFilter)
        update = keyValues.copy()
        update.pop('postId')

        return self._repo.updatePost(searchFilter, update)

    def updateThreadByKeyValues(self, keyValues):
        searchFilter = self._createEQSearchFilter(keyValues, 'threadId')
        self._authorizeUpdateThread(searchFilter)
        update = keyValues.copy()
        update.pop('threadId')

        return self._repo.updateThread(searchFilter, update)

    def _createEQSearchFilter(self, keyValues, fieldname):
        try:
            return self._filter.createFilter(dict(
                field=fieldname, operator='eq', value=[ keyValues[fieldname] ]
            ))
        except Exception as e:
            logging.error(e)
            raise exceptions.IdNotSpecifiedError(f'{fieldname} was missing')

    def _authorizeUpdateUser(self, searchFilter):
        """
        Authorize deletion of users.
        Users are searched from repo using searchFilter.
        
        Args:
            searchFilter(PrimitiveFilter): used to search for entities from repo
        Returns:
            None
        """
        users = self._repo.searchUser(searchFilter)['users']
        self._authorizeUpdate(users)

    def _authorizeUpdatePost(self, searchFilter):
        """
        Authorize deletion of posts.
        Posts are searched from repo using searchFilter.
        
        Args:
            searchFilter(PrimitiveFilter): used to search for entities from repo
        Returns:
            None
        """
        posts = self._repo.searchPost(searchFilter)['posts']
        self._authorizeUpdate(posts)

    def _authorizeUpdateThread(self, searchFilter):
        """
        Authorize deletion of threads.
        Threads are searched from repo using searchFilter.
        
        Args:
            searchFilter(PrimitiveFilter): used to search for entities from repo
        Returns:
            None
        """
        threads = self._repo.searchThread(searchFilter)['threads']
        self._authorizeUpdate(threads)

    def _authorizeUpdate(self, entities):
        """
        authorize current user for deletion of entities
        
        Args:
            entities(list): list of entities to delete
        Returns:
            None
        """
        ownerIds = [ entity['userId'] for entity in entities ]
        session_user = self._session.get_user()
        for ownerId in ownerIds:
            if session_user['userId'] != ownerId:
                logging.error('')
                raise exceptions.UnauthorizedError('Failed to authorize user for update')
