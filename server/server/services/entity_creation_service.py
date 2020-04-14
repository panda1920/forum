# -*- coding: utf-8 -*-
"""
This file houses business logic for entity creation made by apis
"""
import logging

import server.exceptions as exceptions


class EntityCreationService:
    GENERIC_PORTRAIT_IMAGE_URL = 'https://www.seekpng.com/png/detail/365-3651600_default-portrait-image-generic-profile.png'

    def __init__(self, repo, filterClass, session):
        self._repo = repo
        self._filter = filterClass
        self._session = session

    def signup(self, keyValues):
        """
        Create new user entity
        
        Args:
            keyValues(dict): contain information to construct user entity
        Returns:
            dictionary that reports result of operation
        """
        self._checkUserExists(keyValues)
        result = self._createUser(keyValues)
        return result

    def createNewPost(self, keyValues):
        """
        Create new post entity
        
        Args:
            keyValues(dict): contain information to construct post entity
        Returns:
            dictionary that reports result of operation
        """
        self._checkOwnerMatchesSession(keyValues)
        result = self._repo.createPost(keyValues)
        self._updateThreadForNewPost(keyValues, result['createdId'])
        return result

    def createNewThread(self, keyValues):
        """
        Create new thread entity
        
        Args:
            keyValues(dict): contain information to construct thread entity
        Returns:
            dictionary that reports result of operation
        """
        self._checkOwnerMatchesSession(keyValues)
        result = self._repo.createThread(keyValues)
        return result

    def _checkUserExists(self, keyValues):
        if 'userName' not in keyValues:
            logging.error('Failed to create user: key "userName" was not found')
            raise exceptions.EntityValidationError('Failed to create user')

        searchFilter = self._filter.createFilter(dict(
            field='userName',
            operator='eq',
            value=[ keyValues['userName'] ]
        ))
        result = self._repo.searchUser(searchFilter)

        if result['returnCount'] > 0:
            logging.error(
                f'Failed to create user: username { keyValues["userName"] } already exist'
            )
            raise exceptions.DuplicateUserError('Username already exist')

    def _checkOwnerMatchesSession(self, keyValues):
        resource_owner = keyValues.get('userId', None)
        session = self._session.get_user()
        session_user = session.get('userId', None)

        if resource_owner != session_user:
            logging.error(f'Failed to authorize user: {session_user} to create thread')
            raise exceptions.UnauthorizedError('Failed to authorize user')

    def _createUser(self, keyValues):
        atIdx = keyValues['userName'].find('@')
        defaultName = keyValues['userName'][:atIdx]
        defaultImage = self.GENERIC_PORTRAIT_IMAGE_URL

        return self._repo.createUser(dict(
            **keyValues,
            displayName=defaultName,
            imageUrl=defaultImage
        ))

    def _updateThreadForNewPost(self, keyValues, newId):
        searchFilter = self._filter.createFilter(dict(
            field='threadId', operator='eq', value=[ keyValues['threadId'] ]
        ))
        update = dict(increment='posts', lastPostId=newId)
        self._repo.updateThread(searchFilter, update)
