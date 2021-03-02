# -*- coding: utf-8 -*-
"""
This file houses data for testing Post entity
"""
from tests.helpers import create_mock_entities

ID_ATTRIBUTE = 'postId'

DEFAULT_ENTITY_ATTRS = {
    'owner': [ dict(userId='test_id') ]
}
DEFAULT_ALLOWED_ATTRS = {
    '_id': 'test_id',
    'userId': 'test_post',
    'threadId': 'test_thread',
    'postId': 'test_id',
    'content': 'test_value',
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
    **{ k: create_mock_entities(v) for (k, v) in DEFAULT_ENTITY_ATTRS.items() }
}

WRONGTYPE_ATTRS = dict(
    userId=9999,
    postId=9999,
    content=9999,
    owner=9999,
)

ATTRS_NOT_WHITESPACE_OR_EMPTY = [
]
ATTRS_ALLOW_NONE = [
]
ATTRS_RESTRICTED_ATTRS = [
]

TO_SERIALIZE_IGNORE_ATTRS = [
    '_id',
]
TO_SERIALIZE_REQUIRED_ATTRS = [
    'postId',
    'userId',
    'threadId',
    'content',
    'owner',
    'createdAt',
]
TO_SERIALIZE_OPTIONAL_ATTRS = [
    'updatedAt'
]

TO_CREATE_IGNORE_ATTRS = [
    'postId',
    '_id',
    'owner',
    'createdAt',
    'updatedAt',
]
TO_CREATE_REQUIRED_ATTRS = [
    'userId', 'content', 'threadId',
]
TO_CREATE_OPTIONAL_ATTRS = [
]

TO_UPDATE_IGNORE_ATTRS = [
    '_id',
    'postId',
    'userId',
    'threadId',
    'owner',
    'createdAt',
    'updatedAt',
]
TO_UPDATE_REQUIRED_ATTRS = [
]
TO_UPDATE_OPTIONAL_ATTRS = [
    'content'
]
