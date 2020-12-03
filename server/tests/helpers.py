# -*- coding: utf-8 -*-
"""
This file houses useful functions that are used across multiple tests
"""

from tests.mocks import createMockEntity

# default attributes for each entity used in tests
DEFAULT_TESTUSER_ATTRIBUTES = {
    'userId': 'test_user',
}
DEFAULT_TESTPOST_ATTRIBUTES = {
    'postId': 'test_post',
    'userId': 'test_user',
    'threadId': 'test_thread',
}
DEFAULT_TESTTHREAD_ATTRIBUTES = {
    'threadid': 'test_thread',
    'userId': 'test_user',
    'boardId': 'test_board',
    'lastPostId': 'test_post',
}
DEFAULT_TESTBOARD_ATTRIBUTES = {
    'boardId': 'test_board',
    'userId': 'test_user',
}


def create_testuser_attrs(**kwargs):
    """
    Creates test attributes for User entity
    Automates creation of attributes so that required attributes would not be missing, unless explicitly told so
    
    Args:
        kwargs: attributes explicitly set by consumer
    Returns:
        Dict of attribute name: value pairs
    """
    return combine_attributes(DEFAULT_TESTUSER_ATTRIBUTES, kwargs)


def create_testpost_attrs(**kwargs):
    """
    Creates test attributes for Post entity
    Automates creation of attributes so that required attributes would not be missing, unless explicitly told so
    
    Args:
        kwargs: attributes explicitly set by consumer
    Returns:
        Dict of attribute name: value pairs
    """
    return combine_attributes(DEFAULT_TESTPOST_ATTRIBUTES, kwargs)


def create_testthread_attrs(**kwargs):
    """
    Creates test attributes for Thread entity
    Automates creation of attributes so that required attributes would not be missing, unless explicitly told so
    
    Args:
        kwargs: attributes explicitly set by consumer
    Returns:
        Dict of attribute name: value pairs
    """
    return combine_attributes(DEFAULT_TESTTHREAD_ATTRIBUTES, kwargs)


def create_testboard_attrs(**kwargs):
    """
    Creates test attributes for Board entity
    Automates creation of attributes so that required attributes would not be missing, unless explicitly told so
    
    Args:
        kwargs: attributes explicitly set by consumer
    Returns:
        Dict of attribute name: value pairs
    """
    return combine_attributes(DEFAULT_TESTBOARD_ATTRIBUTES, kwargs)


def combine_attributes(default_attributes, kwargs):
    attributes = default_attributes.copy()

    for k, v in kwargs.items():
        attributes[k] = v

    return attributes


def create_mock_entity_fromattrs(attrs):
    """
    Creates a mock entity from a dictionary of attributes.
    All attributes passed can be accessed by the form entity.<attr_name>.
    
    Args:
        attrs(dict): dictionary of attributes
    Returns:
        mocked entity
    """
    entity = createMockEntity()
    for k, v in attrs.items():
        setattr(entity, k, v)

    # need these code so that entities can be serialized
    # without these code, MagicMock cannot be JSONified
    entity.to_serialize.return_value = attrs
    entity._convert_dict_for.return_value = attrs

    return entity


def create_mock_entities(attrset):
    """
    Creates a list of mock entities out of list of attributes.
    
    Args:
        attrset(list): list of attributes for each entity to have
    Returns:
        list of entities
    """
    return [ create_mock_entity_fromattrs(attrs) for attrs in attrset ]
