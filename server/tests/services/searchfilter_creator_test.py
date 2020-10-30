# -*- coding: utf-8 -*-
"""
This file houses tests for searchfilter_creator.py
"""

import pytest

from server.services.searchfilter_creator import SearchFilterCreator
from server.database.filter import PrimitiveFilter, FuzzyStringFilter
from server.database.aggregate_filter import AggregateFilter, OrFilter, AndFilter
from server.entity import User, Post, Thread


class TestUserSearchFilter:
    DEFAULT_KEYVALUES = {
        'search': 'test_user',
        'userId': 'hello',
    }

    def test_create_usersearchShouldCreateOrAndInsideAndFilter(self):
        result_filter = SearchFilterCreator.create_usersearch(self.DEFAULT_KEYVALUES)

        assert isinstance(result_filter, AndFilter)
        assert isinstance(result_filter._filters[0], OrFilter)
        assert isinstance(result_filter._filters[1], AndFilter)

    def test_create_usersearchShouldCreateFuzzyFiltersFromSearchKey(self):
        result_filter = SearchFilterCreator.create_usersearch(self.DEFAULT_KEYVALUES)

        fuzzy_filters = result_filter._filters[0]._filters
        assert len(fuzzy_filters) > 0
        for fuzzy_filter in fuzzy_filters:
            assert isinstance(fuzzy_filter, FuzzyStringFilter)

    def test_create_usersearchShouldCreateFuzzyFiltersForCertainFields(self):
        expected_attributes = SearchFilterCreator.user_fuzzysearchable_attributes
        expected_filters = [
            PrimitiveFilter.createFilter(dict(
                field=attr,
                operator='fuzzy',
                value=[ self.DEFAULT_KEYVALUES['search'] ]
            ))
            for attr in expected_attributes
        ]

        result_filter = SearchFilterCreator.create_usersearch(self.DEFAULT_KEYVALUES)
        
        fuzzy_filters = result_filter._filters[0]._filters
        for f in expected_filters:
            assert f in fuzzy_filters

    def test_create_usersearchShouldCreateFuzzyFilterForMultipleValuesWhenSearchIsSpaceDelimited(self):
        expected_values = ['value1', 'value2', 'value3']
        expected_filter = PrimitiveFilter.createFilter(dict(
            field=SearchFilterCreator.user_fuzzysearchable_attributes[0],
            operator='fuzzy',
            value=expected_values,
        ))
        keyvalues = self.DEFAULT_KEYVALUES.copy()
        keyvalues['search'] = ' '.join(expected_values)

        result_filter = SearchFilterCreator.create_usersearch(keyvalues)

        fuzzy_filters = result_filter._filters[0]._filters
        assert expected_filter in fuzzy_filters

    def test_create_usersearchShouldCreateEmptyFuzzyFilterWhenNoSearch(self):
        keyvalues = { 'userId': 'test_id '}

        result_filter = SearchFilterCreator.create_usersearch(keyvalues)

        fuzzy_filters = result_filter._filters[0]._filters
        assert len(fuzzy_filters) == 0

    def test_create_usersearchShouldCreateNarrowingFilterFromFieldsInKeyvalues(self):
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['userId'] ],
        ))

        result_filter = SearchFilterCreator.create_usersearch(self.DEFAULT_KEYVALUES)

        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 1
        assert narrowing_filters[0] == expected_filter

    def test_create_usersearchShouldIgnoreNonUserAttributeInKeyValues(self):
        ignored_attributes = {
            'hello': 'some_value',
            '!@#%!%!@#': 'some_value',
            '12315123': 'some_value',
        }
        keyvalues = self.DEFAULT_KEYVALUES.copy()
        keyvalues.update(ignored_attributes)
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='userId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['userId'] ],
        ))

        result_filter = SearchFilterCreator.create_usersearch(keyvalues)
        
        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 1
        assert narrowing_filters[0] == expected_filter

    def test_createusersearchShouldCreateEmptyNarrowingFilterWhenNoFields(self):
        keyvalues = { 'search': 'test_value' }

        result_filter = SearchFilterCreator.create_usersearch(keyvalues)

        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 0


class TestPostSearchFilter:
    DEFAULT_KEYVALUES = {
        'search': 'test_post',
        'postId': 'hello',
    }

    def test_create_postsearchShouldCreateOrAndInsideAndFilter(self):
        result_filter = SearchFilterCreator.create_postsearch(self.DEFAULT_KEYVALUES)

        assert isinstance(result_filter, AndFilter)
        assert isinstance(result_filter._filters[0], OrFilter)
        assert isinstance(result_filter._filters[1], AndFilter)

    def test_create_postsearchShouldCreateFuzzyFiltersFromSearchKey(self):
        result_filter = SearchFilterCreator.create_postsearch(self.DEFAULT_KEYVALUES)

        fuzzy_filters = result_filter._filters[0]._filters
        assert len(fuzzy_filters) > 0
        for fuzzy_filter in fuzzy_filters:
            assert isinstance(fuzzy_filter, FuzzyStringFilter)

    def test_create_postsearchShouldCreateFuzzyFiltersForCertainFields(self):
        expected_attributes = SearchFilterCreator.post_fuzzysearchable_attributes
        expected_filters = [
            PrimitiveFilter.createFilter(dict(
                field=attr,
                operator='fuzzy',
                value=[ self.DEFAULT_KEYVALUES['search'] ]
            ))
            for attr in expected_attributes
        ]

        result_filter = SearchFilterCreator.create_postsearch(self.DEFAULT_KEYVALUES)
        
        fuzzy_filters = result_filter._filters[0]._filters
        for f in expected_filters:
            assert f in fuzzy_filters

    def test_create_postsearchShouldCreateFuzzyFilterForMultipleValuesWhenSearchIsSpaceDelimited(self):
        expected_values = ['value1', 'value2', 'value3']
        expected_filter = PrimitiveFilter.createFilter(dict(
            field=SearchFilterCreator.post_fuzzysearchable_attributes[0],
            operator='fuzzy',
            value=expected_values,
        ))
        keyvalues = self.DEFAULT_KEYVALUES.copy()
        keyvalues['search'] = ' '.join(expected_values)

        result_filter = SearchFilterCreator.create_postsearch(keyvalues)

        fuzzy_filters = result_filter._filters[0]._filters
        assert expected_filter in fuzzy_filters

    def test_create_postsearchShouldCreateEmptyFuzzyFilterWhenNoSearch(self):
        keyvalues = { 'postId': 'test_id '}

        result_filter = SearchFilterCreator.create_postsearch(keyvalues)

        fuzzy_filters = result_filter._filters[0]._filters
        assert len(fuzzy_filters) == 0

    def test_create_postsearchShouldCreateNarrowingFilterFromFieldsInKeyvalues(self):
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['postId'] ],
        ))

        result_filter = SearchFilterCreator.create_postsearch(self.DEFAULT_KEYVALUES)

        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 1
        assert narrowing_filters[0] == expected_filter

    def test_create_postsearchShouldIgnoreNonUserAttributeInKeyValues(self):
        ignored_attributes = {
            'hello': 'some_value',
            '!@#%!%!@#': 'some_value',
            '12315123': 'some_value',
        }
        keyvalues = self.DEFAULT_KEYVALUES.copy()
        keyvalues.update(ignored_attributes)
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='postId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['postId'] ],
        ))

        result_filter = SearchFilterCreator.create_postsearch(keyvalues)
        
        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 1
        assert narrowing_filters[0] == expected_filter

    def test_createpostsearchShouldCreateEmptyNarrowingFilterWhenNoFields(self):
        keyvalues = { 'search': 'test_value' }

        result_filter = SearchFilterCreator.create_postsearch(keyvalues)

        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 0


class TestThreadSearchFilter:
    DEFAULT_KEYVALUES = {
        'search': 'test_thread',
        'threadId': 'hello',
    }

    def test_create_threadsearchShouldCreateOrAndInsideAndFilter(self):
        result_filter = SearchFilterCreator.create_threadsearch(self.DEFAULT_KEYVALUES)

        assert isinstance(result_filter, AndFilter)
        assert isinstance(result_filter._filters[0], OrFilter)
        assert isinstance(result_filter._filters[1], AndFilter)

    def test_create_threadsearchShouldCreateFuzzyFiltersFromSearchKey(self):
        result_filter = SearchFilterCreator.create_threadsearch(self.DEFAULT_KEYVALUES)

        fuzzy_filters = result_filter._filters[0]._filters
        assert len(fuzzy_filters) > 0
        for fuzzy_filter in fuzzy_filters:
            assert isinstance(fuzzy_filter, FuzzyStringFilter)

    def test_create_threadsearchShouldCreateFuzzyFiltersForCertainFields(self):
        expected_attributes = SearchFilterCreator.thread_fuzzysearchable_attributes
        expected_filters = [
            PrimitiveFilter.createFilter(dict(
                field=attr,
                operator='fuzzy',
                value=[ self.DEFAULT_KEYVALUES['search'] ]
            ))
            for attr in expected_attributes
        ]

        result_filter = SearchFilterCreator.create_threadsearch(self.DEFAULT_KEYVALUES)
        
        fuzzy_filters = result_filter._filters[0]._filters
        for f in expected_filters:
            assert f in fuzzy_filters

    def test_create_threadsearchShouldCreateFuzzyFilterForMultipleValuesWhenSearchIsSpaceDelimited(self):
        expected_values = ['value1', 'value2', 'value3']
        expected_filter = PrimitiveFilter.createFilter(dict(
            field=SearchFilterCreator.thread_fuzzysearchable_attributes[0],
            operator='fuzzy',
            value=expected_values,
        ))
        keyvalues = self.DEFAULT_KEYVALUES.copy()
        keyvalues['search'] = ' '.join(expected_values)

        result_filter = SearchFilterCreator.create_threadsearch(keyvalues)

        fuzzy_filters = result_filter._filters[0]._filters
        assert expected_filter in fuzzy_filters

    def test_create_threadsearchShouldCreateEmptyFuzzyFilterWhenNoSearch(self):
        keyvalues = { 'threadId': 'test_id '}

        result_filter = SearchFilterCreator.create_threadsearch(keyvalues)

        fuzzy_filters = result_filter._filters[0]._filters
        assert len(fuzzy_filters) == 0

    def test_create_threadsearchShouldCreateNarrowingFilterFromFieldsInKeyvalues(self):
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='threadId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['threadId'] ],
        ))

        result_filter = SearchFilterCreator.create_threadsearch(self.DEFAULT_KEYVALUES)

        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 1
        assert narrowing_filters[0] == expected_filter

    def test_create_threadsearchShouldIgnoreNonUserAttributeInKeyValues(self):
        ignored_attributes = {
            'hello': 'some_value',
            '!@#%!%!@#': 'some_value',
            '12315123': 'some_value',
        }
        keyvalues = self.DEFAULT_KEYVALUES.copy()
        keyvalues.update(ignored_attributes)
        expected_filter = PrimitiveFilter.createFilter(dict(
            field='threadId',
            operator='eq',
            value=[ self.DEFAULT_KEYVALUES['threadId'] ],
        ))

        result_filter = SearchFilterCreator.create_threadsearch(keyvalues)
        
        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 1
        assert narrowing_filters[0] == expected_filter

    def test_createthreadsearchShouldCreateEmptyNarrowingFilterWhenNoFields(self):
        keyvalues = { 'search': 'test_value' }

        result_filter = SearchFilterCreator.create_threadsearch(keyvalues)

        narrowing_filters = result_filter._filters[1]._filters
        assert len(narrowing_filters) == 0
