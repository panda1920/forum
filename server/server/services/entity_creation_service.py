# -*- coding: utf-8 -*-
"""
This file houses business logic for entity creation made by apis
"""

from server.entity.post import NewPost

class EntityCreationService:
    def __init__(self, repo):
        self._repo = repo

    def createNewPost(self, keyValues):
        postProps = self._generateNewPostProps(keyValues)
        self._repo.createPost(postProps)

    def _generateNewPostProps(self, keyValues):
        postProps = {}
        # need to retrieve user from credentials
        postProps['userId'] = '0'
        postFields = NewPost.getFields()
        for field in keyValues:
            if field in postFields:
                postProps[field] = keyValues[field]

        return postProps
