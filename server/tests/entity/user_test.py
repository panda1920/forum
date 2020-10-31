# -*- coding: utf-8 -*-
"""
This file houses tests for User entity
"""

import pytest

from server.entity import User
from server.exceptions import EntityValidationError


DEFAULT_ARGS = dict(
    userId='test_id',
    userName='test@example.com',
    displayName='test',
    password='testpassword',
    imageUrl='www.example.com/image.jpg',
    createdAt=123123.12,
    updatedAt=123123.12,
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
        unknown_attrs = {
            'hello': 'test_value',
            'foo': 'test_value',
            '123123': 'test_value',
            '!!!@#!@#': 'test_value',
        }

        user = User({ **DEFAULT_ARGS, **unknown_attrs })

        for known_attr in DEFAULT_ARGS.keys():
            assert hasattr(user, known_attr)
        for unknown_attr in unknown_attrs.keys():
            assert not hasattr(user, unknown_attr)

    def test_constructionValidatesForType(self):
        wrongtype_attrs = dict(
            userId=9999,
            userName=9999,
            displayName=9999,
            password=9999,
            imageUrl=9999,
        )
        for wrong_attr, value in wrongtype_attrs.items():
            args = DEFAULT_ARGS.copy()
            args.update({ wrong_attr: value })

            with pytest.raises(EntityValidationError):
                User(args)

    def test_constructionValidatesUsername(self):
        args = DEFAULT_ARGS.copy()
        args.update(dict(userName='hello'))  # not an email

        with pytest.raises(EntityValidationError):
            User(args)


class TestConversionMethods:
    @pytest.fixture(scope='function')
    def user(self):
        return User(DEFAULT_ARGS)

    def test_to_serialize(self, user):
        serialized = user.to_serialize()

        for attr, value in serialized.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_serializeIgnoresPrivateInformation(self, user):
        private_attrs = ['_id', 'password', ]

        serialized = user.to_serialize()

        for attr in serialized.items():
            assert attr not in private_attrs

    def test_to_serializeValidatesRequiredAttributes(self, user):
        required_attributes = [
            'userId',
            'userName',
            'displayName',
            'imageUrl',
            'createdAt',
        ]
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            user = User(args)

            with pytest.raises(EntityValidationError):
                user.to_serialize()

    def test_to_serializeRaisesNoExceptionWhenMissingOptionalAttributes(self):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(optional_attribute)
            user = User(args)

            user.to_serialize()

    def test_to_serializeContainsOptionalAttributes(self, user):
        optional_attributes = [
            'updatedAt',
        ]

        for optional_attribute in optional_attributes:
            assert hasattr(user, optional_attribute)

    def test_to_createGeneratesDictForCreation(self, user):
        create_dict = user.to_create()

        for attr, value in create_dict.items():
            assert DEFAULT_ARGS[attr] == value

    def test_to_createValidatesForRequiredAttributes(self):
        required_attributes = ['userName', 'displayName', 'password']
        for required_attribute in required_attributes:
            args = DEFAULT_ARGS.copy()
            args.pop(required_attribute)
            user = User(args)

            with pytest.raises(EntityValidationError):
                user.to_create()

    def test_to_createIgnoresUnnecessaryAttributes(self):
        ignored_args = {
            'userId': 'test_value',
            '_id': 'test_value',
            'createdAt': 123123.12
        }
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
        args = { **DEFAULT_ARGS, **ignored_args }
        user = User(args)

        update_dict = user.to_update()

        for ignored_attr in ignored_args.keys():
            assert ignored_attr not in update_dict

    def test_to_updateGeneratesDictWithOptionalAttributes(self):
        optional_attrs = {
            'displayName': 'test_value',
            'password': 'test_value',
            'imageUrl': 'www.example.com/image.jpg',
        }
        args = { **DEFAULT_ARGS, **optional_attrs }
        user = User(args)

        update_dict = user.to_update()

        for optional_attr in optional_attrs:
            assert optional_attr in update_dict


class TestSearch:
    def test_someattrs_are_fuzzysearchable(self):
        fuzzy_searchables = ['userName', 'displayName']

        for attr in fuzzy_searchables:
            search_rules = User._attribute_description[attr]['search_rules']
            assert search_rules['fuzzy'] is True
