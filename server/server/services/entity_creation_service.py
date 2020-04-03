# -*- coding: utf-8 -*-
"""
This file houses business logic for entity creation made by apis
"""

import server.exceptions as exceptions
from server.entity.post import NewPost


class EntityCreationService:
    GENERIC_PORTRAIT_IMAGE_URL = 'https://www.seekpng.com/png/detail/365-3651600_default-portrait-image-generic-profile.png'

    def __init__(self, repo, filterClass):
        self._repo = repo
        self._filter = filterClass

    def signup(self, keyValues):
        self._checkUserExists(keyValues)
        result = self._createUser(keyValues)
        return dict(result=result)

    def createNewPost(self, keyValues):
        postProps = self._generateNewPostProps(keyValues)
        result = self._repo.createPost(postProps)
        return dict(result=result)

    def _checkUserExists(self, keyValues):
        if 'userName' not in keyValues:
            print('Failed to create user: key "userName" was not found')
            raise exceptions.EntityValidationError('Failed to create user')

        searchFilter = self._filter.createFilter(dict(
            field='userName',
            operator='eq',
            value=[ keyValues['userName'] ]
        ))
        result = self._repo.searchUser(searchFilter)

        if result['returnCount'] > 0:
            print(f'Failed to create user: username { keyValues["userName"] } already exist')
            raise exceptions.DuplicateUserError('Username already exist')

    def _createUser(self, keyValues):
        atIdx = keyValues['userName'].find('@')
        defaultName = keyValues['userName'][:atIdx]
        defaultImage = self.GENERIC_PORTRAIT_IMAGE_URL

        return self._repo.createUser(dict(
            **keyValues,
            displayName=defaultName,
            imageUrl=defaultImage
        ))

    def _generateNewPostProps(self, keyValues):
        postProps = {}
        # need to retrieve user from credentials
        postProps['userId'] = '0'
        postFields = NewPost.getFields()
        for field in keyValues:
            if field in postFields:
                postProps[field] = keyValues[field]

        return postProps
