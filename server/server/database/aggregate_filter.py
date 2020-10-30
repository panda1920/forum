# -*- coding: utf-8 -*-
"""
This file houses aggregate search filters like
AND, OR, NOT
"""

from server.database.filter import Filter


class AggregateFilter(Filter):
    """
    Base class for classes that combines multiple filters to declare
    complicated filter operations.
    Can be nested with each other.
    """

    @staticmethod
    def createFilter(opstring, filters=[]):
        """
        A factory method to create aggregate filters.
        The motivation was to avoid having to call individual constructors
        from where it is used which hopefully decouples code.
        
        Args:
            opstring (string): short string representation of aggregate to create
            filteres (list): list of filters to add under the aggregate being created
        Returns:
            a concrete aggregate filter
        """
        if opstring == 'and':
            return AndFilter(filters)
        elif opstring == 'or':
            return OrFilter(filters)

    def setFilters(self, filters):
        """
        Assign filters to be aggregated under this aggregate
        
        Args:
            filters (list): list of filters, which can be primitive or aggregate
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

    def matches(self, entity):
        """
        Determines if target entity matches the filter
        
        Args:
            entity: entity of some entity
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

    def __len__(self):
        """
        Determines the amount of direct child filter this aggregate contains
        
        Args:
        Returns:
            (int): amount of direct child filter this aggregate contains
        """
        raise NotImplementedError

    def __eq__(self, other):
        """
        Compares logical equality of self with other
        
        Args:
            other: other object
        Returns:
            Boolean
        """
        if not isinstance(other, AggregateFilter):
            return NotImplemented

        return all([
            self.getOpString() == other.getOpString(),
            self._filters == other._filters
        ])


class AndFilter(AggregateFilter):
    """
    Relates filters by AND
    """
    def __init__(self, filters):
        self._filters = filters

    def getOpString(self):
        return 'and'

    def setFilters(self, filters):
        self._filters = filters

    def appendFilter(self, filter):
        self._filters.append(filter)

    def matches(self, entity):
        return all([
            f.matches(entity) for f in self._filters
        ])

    def getMongoFilter(self):
        if len(self._filters) == 0:
            return {}
        else:
            return {
                '$and': [ f.getMongoFilter() for f in self._filters ]
            }

    def __len__(self):
        return len(self._filters)


class OrFilter(AggregateFilter):
    """
    Relates filters by OR
    """
    def __init__(self, filters):
        self._filters = filters

    def getOpString(self):
        return 'or'

    def setFilters(self, filters):
        self._filters = filters

    def appendFilter(self, filter):
        self._filters.append(filter)

    def matches(self, entity):
        if len(self) == 0:
            # any of empty list returns False in python
            # found it more convenient if or filters does not block search
            # when it is empty
            return True
            
        return any([
            f.matches(entity) for f in self._filters
        ])

    def getMongoFilter(self):
        if len(self._filters) == 0:
            return {}
        else:
            return {
                '$or': [ f.getMongoFilter() for f in self._filters ]
            }

    def __len__(self):
        return len(self._filters)
