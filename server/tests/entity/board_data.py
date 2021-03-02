# -*- coding: utf-8 -*-
"""
This file houses data for testing Board entity
"""
from tests.helpers import create_mock_entities

ID_ATTRIBUTE = 'boardId'

DEFAULT_ENTITY_ATTRS = {
    'owner': [ dict(userId='test_id') ],
}
DEFAULT_ALLOWED_ATTRS = {
    '_id': 'test_id',
    'boardId': 'test_board',
    'userId': 'test_user',
    'title': 'test_board_title',
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
    **{ k: create_mock_entities(v) for (k, v) in DEFAULT_ENTITY_ATTRS.items() }
}
WRONGTYPE_ATTRS = dict(
    userId=9999,
    boardId=9999,
    owner=9999,
    title=9999,
    createdAt='11111111',
    updatedAt='11111111',
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
    'boardId',
    'userId',
    'owner',
    'title',
    'createdAt',
]
TO_SERIALIZE_OPTIONAL_ATTRS = [
    'updatedAt',
]

TO_CREATE_IGNORE_ATTRS = [
    '_id',
    'boardId',
    'owner',
    'updatedAt',
    'createdAt',
]
TO_CREATE_REQUIRED_ATTRS = [
]
TO_CREATE_OPTIONAL_ATTRS = [
]

TO_UPDATE_IGNORE_ATTRS = [
    '_id',
    'boardId',
    'userId',
    'owner',
    'createdAt',
]
TO_UPDATE_REQUIRED_ATTRS = [
]
TO_UPDATE_OPTIONAL_ATTRS = [
    'title',
]
