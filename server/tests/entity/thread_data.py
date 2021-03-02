# -*- coding: utf-8 -*-
"""
This file houses data for testing Thread entity
"""
from tests.helpers import create_mock_entities

ID_ATTRIBUTE = 'threadId'

DEFAULT_ENTITY_ATTRS = {
    'owner': [ dict(userId='test_userid'), ],
    'ownerBoard': [ dict(boardId='test_boardid'), ],
    'lastPost': [ dict(postId='test_postid'), ],
}
DEFAULT_ALLOWED_ATTRS = {
    'userId': 'test_thread',
    'boardId': 'test_id',
    'threadId': 'test_id',
    'lastPostId': 'test_id',
    'title': 'Anonymous\'s thread',
    'subject': 'test_subject',
    'increment': 'views',
    'views': 0,
    'postCount': 0,
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
    **{ k: create_mock_entities(v) for (k, v) in DEFAULT_ENTITY_ATTRS.items() }
}

WRONGTYPE_ATTRS = dict(
    userId=9999,
    boardId=9999,
    threadId=9999,
    lastPostId=9999,
    owner=9999,
    ownerBoard=9999,
    lastPost=9999,
    title=9999,
    subject=9999,
    views='test_value',
    postCount='test_value',
    increment=9999,
    createdAt='123123.12',
    updatedAt='123123.12',
)

ATTRS_NOT_WHITESPACE_OR_EMPTY = [
    'subject',
    'title',
]
ATTRS_ALLOW_NONE = [
    'lastPostId'
]
ATTRS_RESTRICTED_ATTRS = [
    { 'name': 'increment', 'values': [ 'postCount', 'views', ] },
]

TO_SERIALIZE_IGNORE_ATTRS = [
    '_id', 'increment'
]
TO_SERIALIZE_REQUIRED_ATTRS = [
    'threadId',
    'boardId',
    'owner',
    'lastPost',
    'title',
    'subject',
    'views',
    'postCount',
    'createdAt',
]
TO_SERIALIZE_OPTIONAL_ATTRS = [
    'updatedAt',
]

TO_CREATE_IGNORE_ATTRS = [
    'threadId',
    '_id',
    'increment',
    'owner',
    'ownerBoard',
    'lastPost',
    'createdAt',
    'updatedAt',
]
TO_CREATE_REQUIRED_ATTRS = [
    'userId',
    'boardId',
    'lastPostId',
    'title',
    'subject',
    'views',
    'postCount',
]
TO_CREATE_OPTIONAL_ATTRS = [
]

TO_UPDATE_IGNORE_ATTRS = [
    '_id',
    'threadId',
    'userId',
    'boardId',
    'owner',
    'ownerBoard',
    'lastPost',
    'createdAt',
    'updatedAt',
]
TO_UPDATE_REQUIRED_ATTRS = [
]
TO_UPDATE_OPTIONAL_ATTRS = [
    'title',
    'subject',
    'lastPostId',
    'views',
    'postCount',
    'increment',
]
