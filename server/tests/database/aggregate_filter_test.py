# -*- coding: utf-8 -*-
"""
This file houses tests for aggregate_filter.py
"""

import pytest
from unittest.mock import create_autospec

from server.database.filter import Filter
import server.database.aggregate_filter as aggregates


class TestAndFilter:
    DEFAULT_OBJECT_PASSEDTO_MATCHES = dict(userId='test_id')

    @pytest.fixture(scope='function')
    def agg(self):
        return aggregates.AggregateFilter.createFilter('and')

    def test_construction(self):
        agg = aggregates.AggregateFilter.createFilter('and')

        assert isinstance(agg, aggregates.AndFilter)

    def test_matchesCallsMatchesOnAllSubFiltersSet(self, agg):
        filters = createMockFilters(4)
        agg.setFilters(filters)

        agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

        for f in filters:
            assert f.matches.call_count == 1
            f.matches.assert_called_with(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

    def test_matchesCallsMatchesOnAllSubFiltersAppended(self, agg):
        filters = createMockFilters(4)
        for f in filters:
            agg.appendFilter(f)

        agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

        for f in filters:
            assert f.matches.call_count == 1
            f.matches.assert_called_with(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

    def test_matchesCallsMatchesOnAllSubFiltersSetThroughConstructor(self):
        filters = createMockFilters(4)
        agg = aggregates.AggregateFilter.createFilter('and', filters)

        agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

        for f in filters:
            assert f.matches.call_count == 1
            f.matches.assert_called_with(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

    def test_lenReturnsNumberOfSubfiltersPassed(self):
        filters = createMockFilters(4)
        agg = aggregates.AggregateFilter.createFilter('and', filters)

        assert len(agg) == 4

    def test_matchesForVariousFilterPatterns(self, agg):
        filterPatterns = [
            createMockFiltersWithReturnValuesForMatches(True, True, True, True),
            createMockFiltersWithReturnValuesForMatches(False, False, False, False),
            createMockFiltersWithReturnValuesForMatches(True, False, False, False),
            createMockFiltersWithReturnValuesForMatches(False, True, True, True),
            createMockFiltersWithReturnValuesForMatches(False, True, False, True),
            createMockFiltersWithReturnValuesForMatches(
                True, True, True, True, True, True, True, True,
            ),
            createMockFiltersWithReturnValuesForMatches(True),
            createMockFiltersWithReturnValuesForMatches(False),
            createMockFiltersWithReturnValuesForMatches(),
        ]
        expectedMatchResult = [
            True,
            False,
            False,
            False,
            False,
            True,
            True,
            False,
            True,
        ]

        for filters, expected in zip(filterPatterns, expectedMatchResult):
            agg.setFilters(filters)
            result = agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

            assert result == expected

    def test_matchesWithAggregates(self, agg):
        mockAgg = create_autospec(aggregates.AggregateFilter)
        mockAgg.matches.return_value = False
        filters = [
            *createMockFiltersWithReturnValuesForMatches(True, True),
            mockAgg
        ]

        agg.setFilters(filters)
        assert agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES) is False

    def test_getMongoFilterWithVariousFilterPatterns(self, agg):
        filterPatterns = [
            createMockFiltersWithReturnValuesForGetMongoFilter(1, 2, 3, 4),
            createMockFiltersWithReturnValuesForGetMongoFilter('11', '22', '33'),
            createMockFiltersWithReturnValuesForGetMongoFilter(2),
            createMockFiltersWithReturnValuesForGetMongoFilter(22.2, 33.3),
            createMockFiltersWithReturnValuesForGetMongoFilter(),
        ]
        expectedMongoExpression = [
            { '$and': [1, 2, 3, 4] },
            { '$and': ['11', '22', '33'] },
            { '$and': [2] },
            { '$and': [22.2, 33.3] },
            {},
        ]

        for filters, expected in zip(filterPatterns, expectedMongoExpression):
            agg.setFilters(filters)
            result = agg.getMongoFilter()

            assert result == expected


class TestOrFilter:
    DEFAULT_OBJECT_PASSEDTO_MATCHES = { 'postId': 1 }

    @pytest.fixture(scope='function')
    def agg(self):
        return aggregates.AggregateFilter.createFilter('or')

    def test_construction(self):
        agg = aggregates.AggregateFilter.createFilter('or')

        assert isinstance(agg, aggregates.OrFilter)

    def test_matchesCallsMatchesOnAllSubFiltersSet(self, agg):
        filters = createMockFilters(4)
        agg.setFilters(filters)

        agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

        for f in filters:
            assert f.matches.call_count == 1
            f.matches.assert_called_with(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

    def test_matchesCallsMatchesOnAllSubFiltersAppended(self, agg):
        filters = createMockFilters(4)
        for f in filters:
            agg.appendFilter(f)

        agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

        for f in filters:
            assert f.matches.call_count == 1
            f.matches.assert_called_with(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

    def test_matchesCallsMatchesOnAllSubFiltersSetThroughConstructor(self):
        filters = createMockFilters(4)
        agg = aggregates.AggregateFilter.createFilter('or', filters)

        agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

        for f in filters:
            assert f.matches.call_count == 1
            f.matches.assert_called_with(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

    def test_lenReturnsNumberOfSubfiltersPassed(self):
        filters = createMockFilters(4)
        agg = aggregates.AggregateFilter.createFilter('or', filters)

        assert len(agg) == 4

    def test_matchesForVariousFilterPatterns(self, agg):
        filterPatterns = [
            createMockFiltersWithReturnValuesForMatches(True, True, True, True),
            createMockFiltersWithReturnValuesForMatches(False, False, False, False),
            createMockFiltersWithReturnValuesForMatches(True, False, False, False),
            createMockFiltersWithReturnValuesForMatches(False, True, True, True),
            createMockFiltersWithReturnValuesForMatches(False, True, False, True),
            createMockFiltersWithReturnValuesForMatches(True),
            createMockFiltersWithReturnValuesForMatches(False),
            createMockFiltersWithReturnValuesForMatches(),
        ]
        expectedMatchResult = [
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
        ]

        for filters, expected in zip(filterPatterns, expectedMatchResult):
            agg.setFilters(filters)
            result = agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES)

            assert result == expected

    def test_matchesWithAggregates(self, agg):
        mockAgg = create_autospec(aggregates.AggregateFilter)
        mockAgg.matches.return_value = False
        filters = [
            *createMockFiltersWithReturnValuesForMatches(True, True),
            mockAgg
        ]

        agg.setFilters(filters)

        assert agg.matches(self.DEFAULT_OBJECT_PASSEDTO_MATCHES) is True

    def test_getMongoFilterWithVariousFilterPatterns(self, agg):
        filterPatterns = [
            createMockFiltersWithReturnValuesForGetMongoFilter(1, 2, 3, 4),
            createMockFiltersWithReturnValuesForGetMongoFilter('11', '22', '33'),
            createMockFiltersWithReturnValuesForGetMongoFilter(2),
            createMockFiltersWithReturnValuesForGetMongoFilter(22.2, 33.3),
            createMockFiltersWithReturnValuesForGetMongoFilter(),
        ]
        expectedMongoExpression = [
            { '$or': [1, 2, 3, 4] },
            { '$or': ['11', '22', '33'] },
            { '$or': [2] },
            { '$or': [22.2, 33.3] },
            {},
        ]

        for filters, expected in zip(filterPatterns, expectedMongoExpression):
            agg.setFilters(filters)
            result = agg.getMongoFilter()

            assert result == expected


# helper functions
def createMockFilters(n):
    return [
        create_autospec(Filter) for n in range(n)
    ]


def createMockFiltersWithReturnValuesForMatches(*values):
    mockFilters = createMockFilters( len(values) )
    for v, f in zip(values, mockFilters):
        f.matches.return_value = v

    return mockFilters


def createMockFiltersWithReturnValuesForGetMongoFilter(*values):
    mockFilters = createMockFilters( len(values) )
    for v, f in zip(values, mockFilters):
        f.getMongoFilter.return_value = v

    return mockFilters
