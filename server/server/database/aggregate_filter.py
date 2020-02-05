# -*- coding: utf-8 -*-
"""
This file houses aggregate search filters like 
AND, OR
"""

class AggregateFilter:
    """
    Base class for classes that combines multiple filters to declare
    complicated filter operations.
    Can be nested with each other.
    """

    @staticmethod
    def createFilter(opstring, filters = []):
        if opstring == 'and':
            return AndFilter(filters)
        elif opstring == 'or':
            return OrFilter(filters)

    def setFilters(self, filters):
        """
        Assign filters to be aggregated under this aggregate
        
        Args:
            filters (list): list of filters
        Returns:
            None
        """
        raise NotImplementedError

    def appendFilter(self, filter):
        """
        Append a filter under this aggregate
        
        Args:
            filter: can be primitive or aggregate
        Returns:
            None
        """
        raise NotImplementedError

    def matches(self, record):
        """
        Determines if target record matches the filter
        
        Args:
            record: record of some entity
        Returns:
            Boolean
        """
        raise NotImplementedError

    def getMongoFilter(self):
        """
        get filter object that is passed to mongodb
        
        Args:
        Returns:
            dict expressing mongo filter
        """
        raise NotImplementedError

class AndFilter(AggregateFilter):
    """
    Relates filters by AND
    """
    def __init__(self, filters):
        self._filters = filters

    def setFilters(self, filters):
        self._filters = filters

    def appendFilter(self, filter):
        self._filters.append(filter)

    def matches(self, record):
        return all([
            f.matches(record) for f in self._filters
        ])

    def getMongoFilter(self):
        if len(self._filters) == 0:
            return {}
        else:
            return {
                '$and': [ f.getMongoFilter() for f in self._filters ]
            }

class OrFilter(AggregateFilter):
    """
    Relates filters by OR
    """
    def __init__(self, filters):
        self._filters = filters

    def __init__(self, filters):
        self._filters = filters

    def setFilters(self, filters):
        self._filters = filters

    def appendFilter(self, filter):
        self._filters.append(filter)

    def matches(self, record):
        return any([
            f.matches(record) for f in self._filters
        ])

    def getMongoFilter(self):
        if len(self._filters) == 0:
            return {}
        else:
            return {
                '$or': [ f.getMongoFilter() for f in self._filters ]
            }