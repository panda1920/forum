# -*- coding: utf-8 -*-
"""
This file houses business logic for entity creation made by apis
"""
import logging

import server.exceptions as exceptions
from server.services.session import SessionService


class EntityCreationService:
    GENERIC_PORTRAIT_IMAGE_URL = 'https://www.seekpng.com/png/detail/365-3651600_default-portrait-image-generic-profile.png'

    def __init__(self, repo, filterClass, context):
        self._repo = repo
        self._filter = filterClass
        self._context = context

    def signup(self, keyValues):
        self._checkUserExists(keyValues)
        result = self._createUser(keyValues)
        return result

    def createNewPost(self, keyValues):
        self._checkOwnerMatchesSession(keyValues)
        result = self._repo.createPost(keyValues)
        return result

    def createNewThread(self, keyValues):
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
        session = self._context.read_session(SessionService.SESSION_USER_KEY)
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

    # def _generateNewPostProps(self, keyValues):
    #     postProps = {}
    #     # need to retrieve user from credentials
    #     postProps['userId'] = '0'
    #     postFields = NewPost.getFields()
    #     for field in keyValues:
    #         if field in postFields:
    #             postProps[field] = keyValues[field]

    #     return postProps
