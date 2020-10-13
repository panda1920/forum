# -*- coding: utf-8 -*-
"""
This file houses class that defines how to sort entities during search retrieval
"""
import logging

from server.exceptions import FieldNotFoundInEntityError

logger = logging.getLogger(__name__)


class Sorter:
    """
    defines an interface of Sorter concrete classes.
    """
    def sort(self, entities):
        """
        Sorts raw entity objects
        
        Args:
            entities(list): entities to sort
        Returns:
            list of sorted entities
        """
        raise NotImplementedError

    def sortMongoCursor(self, cursor):
        """
        Applies sort to mongo cursor
        
        Args:
            cursor: mongo cursor object
        Returns:
            Mongo cursor object
        """
        raise NotImplementedError


class AscendingSorter(Sorter):
    """
    Sorts entities in ascending order
    """
    _order = 1

    def __init__(self, field):
        self._field = field

    def sort(self, entities):
        try:
            return sorted(
                entities,
                key=lambda entity: getattr(entity, self._field),
            )
        except AttributeError:
            logger.error(f'Unable to find field {self._field} in entity; failed to sort')
            raise FieldNotFoundInEntityError('Failed to sort entity')

    def sortMongoCursor(self, cursor):
        cursor.sort([ (self._field, self._order) ])
        return cursor
    
    def __eq__(self, other):
        if isinstance(other, AscendingSorter):
            return all([
                self._order == other._order,
                self._field == other._field,
            ])
        return NotImplemented


class DescendingSorter(Sorter):
    """
    Sorts entities in descending order
    """
    _order = -1

    def __init__(self, field):
        self._field = field

    def sort(self, entities):
        try:
            return sorted(
                entities,
                key=lambda entity: getattr(entity, self._field),
                reverse=True
            )
        except AttributeError:
            logger.error(f'Unable to find field {self._field} in entity; failed to sort')
            raise FieldNotFoundInEntityError('Failed to sort entity')

    def sortMongoCursor(self, cursor):
        cursor.sort([ (self._field, self._order) ])
        return cursor

    def __eq__(self, other):
        if isinstance(other, DescendingSorter):
            return all([
                self._order == other._order,
                self._field == other._field,
            ])
        return NotImplemented


class NullSorter(Sorter):
    """
    Sorter class that does no sorting whatsoever
    A null object pattern
    """
    def sort(self, entities):
        return entities
    
    def sortMongoCursor(self, cursor):
        return cursor

    def __eq__(self, other):
        if isinstance(other, NullSorter):
            return True
        return NotImplemented
