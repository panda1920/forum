# -*- coding: utf-8 -*-
"""
This file houses business logic related to entity update
"""

import logging

import server.exceptions as exceptions

logger = logging.getLogger(__name__)


class UpdateService:
    """
    Class that provides methods to update entities.
    Includes most of the business logic related to update operations.
    """
    def __init__(self, repo, PrimitiveFilter, session):
        self._repo = repo
        self._filter = PrimitiveFilter
        self._session = session

    def updateUser(self, user):
        """
        Updates a single user.
        
        Args:
            user(entity): A user entity object
        Returns:
            dict that reports result of updating repository
        """
        logger.info('Updating User entity')

        searchFilter = self._create_eqfilter(user, 'userId')
        self._authorizeUpdateUser(searchFilter)

        return self._repo.updateUser(searchFilter, user)

    def updatePost(self, post):
        """
        Updates a single post.
        
        Args:
            post(entity): A post entity object
        Returns:
            dict that reports result of updating repository
        """
        logger.info('Updating Post entity')

        searchFilter = self._create_eqfilter(post, 'postId')
        self._authorizeUpdatePost(searchFilter)

        return self._repo.updatePost(searchFilter, post)

    def updateThread(self, thread):
        """
        Updates a single thread.
        
        Args:
            thread(entity): A thread entity object
        Returns:
            dict that reports result of updating repository
        """
        logger.info('Updating Thread entity')

        searchFilter = self._create_eqfilter(thread, 'threadId')
        self._authorizeUpdateThread(searchFilter)

        return self._repo.updateThread(searchFilter, thread)

    def _create_eqfilter(self, entity, fieldname):
        try:
            return self._filter.createFilter(dict(
                field=fieldname, operator='eq', value=[ getattr(entity, fieldname) ]
            ))
        except AttributeError:
            logger.warning('Failed to update user')
            logger.warning('Field: %s was missing', fieldname)
            raise exceptions.IdNotSpecifiedError('Failed to update user')

    def _authorizeUpdateUser(self, searchFilter):
        """
        Authorize update of users.
        Users are searched from repo using searchFilter.
        
        Args:
            searchFilter(PrimitiveFilter): used to search for entities from repo
        Returns:
            None
        """
        logger.debug('Authorizing update of User entity')

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
        logger.debug('Authorizing update of Post entity')

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
        logger.debug('Authorizing update of Thread entity')

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
        ownerIds = [ entity.userId for entity in entities ]
        session_userid = self._session.get_user().userId
        for ownerId in ownerIds:
            if session_userid != ownerId:
                logger.warning('Failed to authorize user')
                logger.warning(f'owner: {ownerId}, session user: {session_userid}')
                raise exceptions.UnauthorizedError('Failed to authorize user for update')
