# -*- coding: utf-8 -*-
"""
This file houses class dedicated to create complicated filter structures
which will then be passed to repository objects
"""

from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.entity import User, Post, Thread, Board


def extract_fuzzy_attributes(entity):
    """
    Lists out attributes of an entity that are searchable by fuzzy search
    
    Args:
        entity(class): an entity class like User of Post
    Returns:
        list of attribute names in string
    """
    fuzzy_attributes = []

    for attr_name, attr in entity._attribute_description.items():
        search_rules = attr.get('search_rules', None)
        if not search_rules:
            continue

        if search_rules.get('fuzzy', False) is True:
            fuzzy_attributes.append(attr_name)

    return fuzzy_attributes


class SearchFilterCreator:
    """
    The intent of this class was to break off filter creating logic that was inside
    search_service.

    Class dedicated to create a complicated filter structure from
    query string coming from the front end.
    The created filter can then be passed to a repository object to search for entities.
    """
    user_attributes = User._attribute_description.keys()
    user_fuzzysearchable_attributes = extract_fuzzy_attributes(User)
    post_attributes = Post._attribute_description.keys()
    post_fuzzysearchable_attributes = extract_fuzzy_attributes(Post)
    thread_attributes = Thread._attribute_description.keys()
    thread_fuzzysearchable_attributes = extract_fuzzy_attributes(Thread)
    board_attributes = Board._attribute_description.keys()
    board_fuzzysearchable_attributes = extract_fuzzy_attributes(Board)

    @classmethod
    def create_usersearch(cls, keyvalues):
        return cls.create_searchfilters(
            keyvalues,
            cls.user_attributes,
            cls.user_fuzzysearchable_attributes,
        )

    @classmethod
    def create_postsearch(cls, keyvalues):
        return cls.create_searchfilters(
            keyvalues,
            cls.post_attributes,
            cls.post_fuzzysearchable_attributes,
        )

    @classmethod
    def create_threadsearch(cls, keyvalues):
        return cls.create_searchfilters(
            keyvalues,
            cls.thread_attributes,
            cls.thread_fuzzysearchable_attributes,
        )

    @classmethod
    def create_boardsearch(cls, keyvalues):
        return cls.create_searchfilters(
            keyvalues,
            cls.board_attributes,
            cls.board_fuzzysearchable_attributes,
        )

    @classmethod
    def create_searchfilters(cls, keyvalues, entity_attrs, fuzzy_attrs):
        search_term = cls._extract_search_term(keyvalues)
        attrs = cls._extract_valid_attrs(keyvalues, entity_attrs)

        fuzzy_filters = cls._create_fuzzyfilters_for(
            search_term,
            fuzzy_attrs
        )
        narrowing_filters = cls._create_narrowing_filters_for(keyvalues, attrs)

        return AggregateFilter.createFilter('and', [
            fuzzy_filters,
            narrowing_filters,
        ])

    @classmethod
    def _extract_search_term(cls, keyvalues):
        search_value = keyvalues.get('search', None)
        if search_value:
            return search_value.split(' ')
        else:
            return []

    @classmethod
    def _extract_valid_attrs(cls, keyvalues, entity_attrs):
        valid_attrs = []
        for attr in entity_attrs:
            if attr in keyvalues:
                valid_attrs.append(attr)

        return valid_attrs

    @classmethod
    def _create_fuzzyfilters_for(cls, search_term, attrs):
        if not search_term:
            fuzzy_filters = []
        else:
            fuzzy_filters = [
                PrimitiveFilter.createFilter(dict(
                    field=attr,
                    operator='fuzzy',
                    value=search_term
                ))
                for attr in attrs
            ]

        return AggregateFilter.createFilter('or', fuzzy_filters)

    @classmethod
    def _create_narrowing_filters_for(cls, keyvalues, attrs):
        narrowing_filters = [
            PrimitiveFilter.createFilter(dict(
                field=attr,
                operator='eq',
                value=[ keyvalues[attr] ],
            ))
            for attr in attrs
        ]
        return AggregateFilter.createFilter('and', narrowing_filters)
