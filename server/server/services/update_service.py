# -*- coding: utf-8 -*-
"""
This file houses business logic related to entity update
"""

import logging

import server.exceptions as exceptions


class UpdateService:
    """
    Class that provides methods to update entities.
    Includes most of the business logic related to update operations.
    """
    def __init__(self, repo, PrimitiveFilter):
        self._repo = repo
        self._filter = PrimitiveFilter

    def updateUserByKeyValues(self, keyValues):
        searchFilter = self._createEQSearchFilter(keyValues, 'userId')
        update = keyValues.copy().pop('userId')

        return self._repo.updateUser(searchFilter, update)

    def updatePostByKeyValues(self, keyValues):
        searchFilter = self._createEQSearchFilter(keyValues, 'postId')
        update = keyValues.copy().pop('postId')

        return self._repo.updatePost(searchFilter, update)

    def _createEQSearchFilter(self, keyValues, fieldname):
        try:
            return self._filter.createFilter(dict(
                field=fieldname, operator='eq', value=[ keyValues[fieldname] ]
            ))
        except Exception as e:
            logging.error(e)
            raise exceptions.IdNotSpecifiedError(f'{fieldname} was missing')
