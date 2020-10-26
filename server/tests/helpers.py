# -*- coding: utf-8 -*-
"""
This file houses useful functions that are used across multiple tests
"""

from tests.mocks import createMockEntity


def create_mock_entities(attrset):
    """
    Creates a list of mock entities out of list of attributes.
    
    Args:
        attrset(list): list of attributes for each entity to have
    Returns:
        list of entities
    """
    entities = [ createMockEntity() for n in attrset ]
    for entity, attrs in zip(entities, attrset):
        for k, v in attrs.items():
            setattr(entity, k, v)

    return entities
