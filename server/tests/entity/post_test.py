# -*- coding: utf-8 -*-
"""
This file houses tests for Post entity
"""

import pytest
import json

from server.entity import Post
from server.exceptions import EntityValidationError
from tests.mocks import createMockEntity

DEFAULT_ARGS = {
    '_id': 'test_id',
    'userId': 'test_post',
    'postId': 'test_id',
    'content': 'test_value',
    'owner': [],
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
    MOCK_USER_ATTRS = { 'userID': 'test_user_id' }

    @pytest.fixture(scope='function')
    def post(self):
        post = Post(DEFAULT_ARGS)
        mock_user = createMockEntity()
        mock_user._convert_dict_for.return_value = self.MOCK_USER_ATTRS
        post.owner = [ mock_user ]

        return post

    def test_to_json(self, post):
        json_string = post.to_json()

        json_dict = json.loads(json_string)
        for attr, value in json_dict.items():
            if attr == 'owner':
                assert [ self.MOCK_USER_ATTRS ] == value
            else:
                assert DEFAULT_ARGS[attr] == value

    def test_to_jsonIgnoresPrivateInformation(self, post):
        private_attrs = ['_id', ]

        json_string = post.to_json()

        json_dict = json.loads(json_string)
        for attr, value in json_dict.items():
            assert attr not in private_attrs

    def test_to_jsonCallsConvertDictForEachOwners(self, post):
        owners = post.owner

        try:
            post.to_json()
        except Exception:
            # ignore failed serialization during tests
            pass

        for owner in owners:
            assert len(owner._convert_dict_for.call_args_list) > 0
            arg1, *_ = owner._convert_dict_for.call_args_list[0][0]
            assert arg1 == 'to_json'

    def test_to_jsonValidatesRequiredAttributes(self, post):
        required_attributes = [
            'postId',
            'userId',
            'content',
            'owner',
            'createdAt',
            'updatedAt',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            post = Post(args)

            with pytest.raises(EntityValidationError):
                post.to_json()

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
