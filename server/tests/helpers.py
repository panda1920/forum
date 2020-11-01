# -*- coding: utf-8 -*-
"""
This file houses useful functions that are used across multiple tests
"""

from tests.mocks import createMockEntity


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
