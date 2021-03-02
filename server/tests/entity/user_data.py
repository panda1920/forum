# -*- coding: utf-8 -*-
"""
This file houses data for testing User entity
"""
from tests.helpers import create_mock_entities

ID_ATTRIBUTE = 'userId'

DEFAULT_ENTITY_ATTRS = {
}
DEFAULT_ALLOWED_ATTRS = {
    'id': 'test_id',
    'userId': 'test_id',
    'userName': 'test@example.com',
    'displayName': 'test',
    'password': 'testpassword',
    'imageUrl': 'www.example.com/image.jpg',
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
    **{ k: create_mock_entities(v) for (k, v) in DEFAULT_ENTITY_ATTRS.items() }
}
WRONGTYPE_ATTRS = dict(
    userId=9999,
    userName=9999,
    displayName=9999,
    password=9999,
    imageUrl=9999,
)

ATTRS_NOT_WHITESPACE_OR_EMPTY = [
]
ATTRS_ALLOW_NONE = [
]
ATTRS_RESTRICTED_ATTRS = [
]

TO_SERIALIZE_IGNORE_ATTRS = [
    '_id', 'password',
]
TO_SERIALIZE_REQUIRED_ATTRS = [
    'userId',
    'userName',
    'displayName',
    'imageUrl',
    'createdAt',
]
TO_SERIALIZE_OPTIONAL_ATTRS = [
    'updatedAt',
]

TO_CREATE_IGNORE_ATTRS = [
    '_id', 'userId', 'createdAt', 'updatedAt',
]
TO_CREATE_REQUIRED_ATTRS = [
    'userName', 'displayName', 'password',
]
TO_CREATE_OPTIONAL_ATTRS = [
    'imageUrl',
]

TO_UPDATE_IGNORE_ATTRS = [
    '_id',
    'userId',
    'userName',
    'createdAt',
    'updatedAt',
]
TO_UPDATE_REQUIRED_ATTRS = [

]
TO_UPDATE_OPTIONAL_ATTRS = [
    'displayName',
    'password',
    'imageUrl',
]
