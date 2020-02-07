# -*- coding: utf-8 -*-
"""
This file houses business logic for entity creation made by apis
"""

import server.exceptions as exceptions
from server.entity.post import NewPost

class EntityCreationService:
    def __init__(self, repo, filterClass):
        self._repo = repo
        self._filter = filterClass

    def signup(self, keyValues):
        self._checkUserExists(keyValues)
        self._createUser(keyValues)

    def createNewPost(self, keyValues):
        postProps = self._generateNewPostProps(keyValues)
        self._repo.createPost(postProps)

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

        self._repo.createUser(dict(
            **keyValues,
            displayName=defaultName,
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
