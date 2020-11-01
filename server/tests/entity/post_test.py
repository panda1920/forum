# -*- coding: utf-8 -*-
"""
This file houses tests for Post entity
"""

import pytest

from server.entity import Post
from server.exceptions import EntityValidationError
from tests.helpers import create_mock_entities

DEFAULT_OWNER_ATTRS = [
    dict(userId='test_id')
]

DEFAULT_ARGS = {
    '_id': 'test_id',
    'userId': 'test_post',
    'postId': 'test_id',
    'content': 'test_value',
    'owner': create_mock_entities(DEFAULT_OWNER_ATTRS),
    'createdAt': 123123.12,
    'updatedAt': 123123.12,
}


class TestUserCreation:
    def test_construction_with_kwargs(self):
        post = Post(**DEFAULT_ARGS)

        assert post.postId == DEFAULT_ARGS['postId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(post, attr_name) == attr_value

    def test_construction_with_dict(self):
        post = Post(DEFAULT_ARGS)

        assert post.postId == DEFAULT_ARGS['postId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(post, attr_name) == attr_value

    def test_constructionIgnoresUnknownAttributes(self):
        unknown_attrs = {
            'hello': 'test_value',
            'foo': 'test_value',
            '123123': 'test_value',
            '!!!@#!@#': 'test_value',
        }

        post = Post({ **DEFAULT_ARGS, **unknown_attrs })

        for known_attr in DEFAULT_ARGS.keys():
            assert hasattr(post, known_attr)
        for unknown_attr in unknown_attrs.keys():
            assert not hasattr(post, unknown_attr)

    def test_constructionValidatesForType(self):
        wrongtype_attrs = dict(
            userId=9999,
            postId=9999,
            content=9999,
            owner=9999,
        )
        for wrong_attr, value in wrongtype_attrs.items():
            args = DEFAULT_ARGS.copy()
            args.update({ wrong_attr: value })

            with pytest.raises(EntityValidationError):
                Post(args)


class TestConversionMethods:
    @pytest.fixture(scope='function')
    def post(self):
        post = Post(DEFAULT_ARGS)

        for owner in post.owner:
            owner.reset_mock()

        return post

    def test_to_serialize(self, post):
        serialized = post.to_serialize()

        for attr, value in serialized.items():
            if attr == 'owner':
                assert DEFAULT_OWNER_ATTRS == value
            else:
                assert DEFAULT_ARGS[attr] == value

    def test_to_serializeCallsConvertDictForEachOwners(self, post):
        owners = post.owner

        try:
            post.to_serialize()
        except Exception:
            # ignore failed serialization during tests
            pass

        for owner in owners:
            assert owner._convert_dict_for.call_count == 1
            arg1, *_ = owner._convert_dict_for.call_args_list[0][0]
            assert arg1 == 'to_serialize'

    def test_to_serializeIgnoresPrivateInformation(self, post):
        private_attrs = ['_id', ]

        serialized = post.to_serialize()

        for attr in serialized.keys():
            assert attr not in private_attrs

    def test_to_serializeValidatesRequiredAttributes(self):
        required_attributes = [
            'postId',
            'userId',
            'content',
            'owner',
            'createdAt',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            post = Post(args)

            with pytest.raises(EntityValidationError):
                post.to_serialize()

    def test_to_serializeRaisesNoExceptionWhenMissingOptionalAttributes(self):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(optional_attribute)
            post = Post(args)

            post.to_serialize()

    def test_to_serializeContainsOptionalAttributes(self, post):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            assert hasattr(post, optional_attribute)

    def test_to_createGeneratesDictForCreation(self, post):
        create_dict = post.to_create()

        for attr, value in create_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_createValidatesForRequiredAttributes(self):
        required_attributes = ['userId', 'content', ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            post = Post(args)

            with pytest.raises(EntityValidationError):
                post.to_create()

    def test_to_createIgnoresUnnecessaryAttributes(self, post):
        ignored_attrs = [
            'postId',
            '_id',
            'owner',
            'createdAt',
            'updatedAt',
        ]

        create_dict = post.to_create()
        
        for attr in ignored_attrs:
            assert attr not in create_dict

    def test_to_updateGeneratesDictForUpdate(self, post):
        update_dict = post.to_update()

        for attr, value in update_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_updateIgnoresUnnecessaryAttributes(self, post):
        ignored_attrs = [
            '_id',
            'postId',
            'userId',
            'owner',
            'createdAt',
            'updatedAt',
        ]

        update_dict = post.to_update()

        for ignored_attr in ignored_attrs:
            assert ignored_attr not in update_dict

    def test_to_updateGeneratesDictWithOptionalAttributes(self, post):
        optional_attrs = [
            'content',
        ]

        update_dict = post.to_update()

        for optional_attr in optional_attrs:
            assert optional_attr in update_dict
            assert DEFAULT_ARGS[optional_attr] == update_dict[optional_attr]


class TestSearch:
    def test_someattrs_are_fuzzysearchable(self):
        fuzzy_searchables = ['content']

        for attr in fuzzy_searchables:
            search_rules = Post._attribute_description[attr]['search_rules']
            assert search_rules['fuzzy'] is True
