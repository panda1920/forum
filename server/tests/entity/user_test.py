# -*- coding: utf-8 -*-
"""
This file houses tests for User entity
"""

import pytest
import json

from server.entity.user import User
from server.exceptions import EntityValidationError


DEFAULT_ARGS = dict(
    userId='test_id',
    userName='test@example.com',
    displayName='test',
    password='testpassword',
    imageUrl='www.example.com/image.jpg',
)


class TestUserCreation:
    def test_construction_with_kwargs(self):
        user = User(**DEFAULT_ARGS)

        assert user.userId == DEFAULT_ARGS['userId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(user, attr_name) == attr_value

    def test_construction_with_dict(self):
        user = User(DEFAULT_ARGS)

        assert user.userId == DEFAULT_ARGS['userId']
        for attr_name, attr_value in DEFAULT_ARGS.items():
            assert getattr(user, attr_name) == attr_value

    def test_constructionIgnoresUnknownAttributes(self):
        unknown_args = {
            'hello': 'test_value',
            'foo': 'test_value',
            '123123': 'test_value',
            '!!!@#!@#': 'test_value',
        }

        user = User({ **DEFAULT_ARGS, **unknown_args })
        print(user.__dict__)

        for attr in DEFAULT_ARGS.keys():
            assert hasattr(user, attr)
        for attr in unknown_args.keys():
            assert not hasattr(user, attr)

    def test_constructionValidatesUsername(self):
        args = DEFAULT_ARGS.copy()
        args.update(dict(userName='hello'))  # not an email

        with pytest.raises(EntityValidationError):
            User(args)


class TestConversionMethods:
    @pytest.fixture(scope='function')
    def user(self):
        return User(DEFAULT_ARGS)

    def test_to_json(self, user):
        json_string = user.to_json()

        json_dict = json.loads(json_string)
        for attr, value in json_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_jsonIgnoresPrivateInformation(self, user):
        private_attrs = ['_id', 'password', ]

        json_string = user.to_json()

        json_dict = json.loads(json_string)
        for attr, value in json_dict.items():
            assert attr not in private_attrs

    def test_to_createGeneratesDictForCreation(self, user):
        create_dict = user.to_create()

        for attr, value in create_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_createValidatesForRequiredAttributes(self):
        required_attributes = ['userId', 'userName', 'displayName', 'password']
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            user = User(args)

            with pytest.raises(EntityValidationError):
                user.to_create()

    def test_to_createIgnoresUnnecessaryAttributes(self):
        ignored_args = { '_id': 'test_value', 'createdAt': 123123.12 }
        args = {**DEFAULT_ARGS, **ignored_args }
        user = User(args)

        create_dict = user.to_create()
        for attr in ignored_args.keys():
            assert attr not in create_dict

    def test_to_updateGeneratesDictForUpdate(self, user):
        update_dict = user.to_update()

        for attr, value in update_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_updateIgnoresUnnecessaryAttributes(self):
        ignored_args = {
            '_id': 'test_value',
            'userId': 'test_value',
            'userName': 'test@example.com',
            'createdAt': 123123.12,
            'updatedAt': 123123.12,
        }
        args = {**DEFAULT_ARGS, **ignored_args }
        user = User(args)

        update_dict = user.to_update()
        for attr in ignored_args.keys():
            assert attr not in update_dict
