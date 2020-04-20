# -*- coding: utf-8 -*-
"""
This file houses class that defines how to sort entities during search retrieval
"""
import logging

from server.exceptions import FieldNotFoundInEntityError


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

    def __eq__(self, other):
        return all([
            self._order == other._order,
            self._field == other._field,
        ])


class AscendingSorter(Sorter):
    """
    Sorts entities in ascending order
    """
    _order = 1

    def __init__(self, field):
        self._field = field

    def sort(self, entities):
        try:
            return sorted(entities, key=lambda entity: entity[self._field])
        except KeyError:
            logging.error(f'Unable to find field {self._field} in entity; failed to sort')
            raise FieldNotFoundInEntityError('Failed to sort entity')

    def sortMongoCursor(self, cursor):
        cursor.sort([ (self._field, self._order) ])
        return cursor


class DescendingSorter(Sorter):
    """
    Sorts entities in descending order
    """
    _order = -1

    def __init__(self, field):
        self._field = field

    def sort(self, entities):
        try:
            return sorted(entities, key=lambda entity: entity[self._field], reverse=True)
        except KeyError:
            logging.error(f'Unable to find field {self._field} in entity; failed to sort')
            raise FieldNotFoundInEntityError('Failed to sort entity')

    def sortMongoCursor(self, cursor):
        cursor.sort([ (self._field, self._order) ])
        return cursor


class NullSorter(Sorter):
    """
    Sorter class that does no sorting whatsoever
    A null object pattern
    """
    def sort(self, entities):
        return entities
    
    def sortMongoCursor(self, cursor):
        return cursor
