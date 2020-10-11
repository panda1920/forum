# -*- coding: utf-8 -*-
"""
This file houses tests for Post entity
"""

import pytest
import json

from server.entity import Post
from server.exceptions import EntityValidationError


DEFAULT_ARGS = dict(
    userId='test_post',
    postId='test_id',
    content='test_value',
    createdAt=123123.12,
    updatedAt=123123.12,
)


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
        )
        for wrong_attr, value in wrongtype_attrs.items():
            args = DEFAULT_ARGS.copy()
            args.update({ wrong_attr: value })

            with pytest.raises(EntityValidationError):
                Post(args)


class TestConversionMethods:
    @pytest.fixture(scope='function')
    def post(self):
        return Post(DEFAULT_ARGS)

    def test_to_json(self, post):
        json_string = post.to_json()

        json_dict = json.loads(json_string)
        for attr, value in json_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_jsonIgnoresPrivateInformation(self, post):
        private_attrs = ['_id', ]

        json_string = post.to_json()

        json_dict = json.loads(json_string)
        for attr, value in json_dict.items():
            assert attr not in private_attrs

    def test_to_jsonValidatesRequiredAttributes(self, post):
        required_attributes = [
            'postId',
            'userId',
            'content',
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

    def test_to_createIgnoresUnnecessaryAttributes(self):
        ignored_args = {
            'postId': 'test_value',
            '_id': 'test_value',
            'createdAt': 123123.12
        }
        args = {**DEFAULT_ARGS, **ignored_args }
        post = Post(args)

        create_dict = post.to_create()
        
        for attr in ignored_args.keys():
            assert attr not in create_dict

    def test_to_updateGeneratesDictForUpdate(self, post):
        update_dict = post.to_update()

        for attr, value in update_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_updateIgnoresUnnecessaryAttributes(self):
        ignored_args = {
            '_id': 'test_value',
            'postId': 'test_value',
            'userId': 'test_value',
            'createdAt': 123123.12,
            'updatedAt': 123123.12,
        }
        args = { **DEFAULT_ARGS, **ignored_args }
        post = Post(args)

        update_dict = post.to_update()

        for ignored_attr in ignored_args.keys():
            assert ignored_attr not in update_dict

    def test_to_updateGeneratesDictWithOptionalAttributes(self):
        optional_attrs = {
            'content': 'test_value'
        }
        args = { **DEFAULT_ARGS, **optional_attrs }
        post = Post(args)

        update_dict = post.to_update()

        for optional_attr in optional_attrs:
            assert optional_attr in update_dict
