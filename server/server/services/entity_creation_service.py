# -*- coding: utf-8 -*-
"""
This file houses business logic for entity creation
"""
import logging

import server.exceptions as exceptions
from server.entity import Thread

logger = logging.getLogger(__name__)


class EntityCreationService:
    GENERIC_PORTRAIT_IMAGE_URL = 'https://www.seekpng.com/png/detail/365-3651600_default-portrait-image-generic-profile.png'

    def __init__(self, repo, filterClass, session):
        self._repo = repo
        self._filter = filterClass
        self._session = session

    def signup(self, user):
        """
        Create new user entity
        
        Args:
            user: User entity object
        Returns:
            dictionary that reports result of operation
        """
        self._checkUserExists(user)
        return self._createUser(user)

    def createNewPost(self, post):
        """
        Create new post entity
        
        Args:
            post: Post entity object
        Returns:
            dictionary that reports result of operation
        """
        self._checkOwnerMatchesSession(post)
        result = self._repo.createPost(post)
        self._updateThreadForNewPost(post, result['createdId'])
        return result

    def createNewThread(self, thread):
        """
        Create new thread entity
        
        Args:
            thead: Thread entity object
        Returns:
            dictionary that reports result of operation
        """
        self._checkOwnerMatchesSession(thread)
        return self._createThread(thread)

    def _checkUserExists(self, user):
        try:
            username = user.userName
        except AttributeError:
            logger.error('User is missing username')
            raise exceptions.EntityValidationError('User is missing username')

        searchFilter = self._filter.createFilter(dict(
            field='userName',
            operator='eq',
            value=[ username ]
        ))
        result = self._repo.searchUser(searchFilter)

        if result['returnCount'] > 0:
            logger.error(
                f'Failed to create user: username { username } already exist'
            )
            raise exceptions.DuplicateUserError('Username already exist')

    def _checkOwnerMatchesSession(self, entity):
        resource_owner = getattr(entity, 'userId', None)
        session = self._session.get_user()
        session_user = session.get('userId', None)

        if resource_owner != session_user:
            logger.error(f'Failed to authorize user: {session_user} to create thread')
            raise exceptions.UnauthorizedError('Failed to authorize user')

    def _createUser(self, user):
        atIdx = user.userName.find('@')
        defaultName = user.userName[:atIdx]

        user.displayName = defaultName
        user.imageUrl = self.GENERIC_PORTRAIT_IMAGE_URL

        return self._repo.createUser(user)

    def _createThread(self, thread):
        thread.lastPostId = None
        thread.views = 0
        thread.postCount = 0

        return self._repo.createThread(thread)

    def _updateThreadForNewPost(self, post, newId):
        searchFilter = self._filter.createFilter(dict(
            field='threadId', operator='eq', value=[ post.threadId ]
        ))
        update = Thread(increment='postCount', lastPostId=newId)
        self._repo.updateThread(searchFilter, update)
