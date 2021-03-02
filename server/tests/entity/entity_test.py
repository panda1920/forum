# -*- coding: utf-8 -*-
"""
This file houses tests for entities
"""
import pytest

import server.entity as entity
import tests.entity.user_data as user_data
import tests.entity.post_data as post_data
import tests.entity.thread_data as thread_data
import tests.entity.board_data as board_data
from server.exceptions import EntityValidationError

UNKNOWN_ATTRS = {
    'hello': 'test_value',
    'foo': 'test_value',
    '123123': 'test_value',
    '!!!@#!@#': 'test_value',
}

RANDOM_VALUES = [ 123456789, 'random_VALUE', '12312312', '!@#!@$!@', ]

test_param_names = 'Entity,test_data'
test_params = [
    ( entity.User, user_data),
    ( entity.Post, post_data, ),
    ( entity.Thread, thread_data, ),
    ( entity.Board, board_data, ),
]
test_types = ['User', 'Post', 'Thread', 'Board']


@pytest.mark.parametrize(test_param_names, test_params, ids=test_types)
class TestEntityCreation:
    def test_construction_with_kwargs(self, Entity, test_data):
        allowed_attrs = test_data.DEFAULT_ALLOWED_ATTRS
        id_attribute = test_data.ID_ATTRIBUTE

        entity = Entity(**allowed_attrs)

        assert getattr(entity, id_attribute) == allowed_attrs[id_attribute]
        for attr_name, attr_value in allowed_attrs.items():
            assert getattr(entity, attr_name) == attr_value

    def test_construction_with_dict(self, Entity, test_data):
        allowed_attrs = test_data.DEFAULT_ALLOWED_ATTRS
        id_attribute = test_data.ID_ATTRIBUTE

        entity = Entity(allowed_attrs)

        assert getattr(entity, id_attribute) == allowed_attrs[id_attribute]
        for attr_name, attr_value in allowed_attrs.items():
            assert getattr(entity, attr_name) == attr_value

    def test_constructionIncludesUnknownAttributes(self, Entity, test_data):
        allowed_attrs = test_data.DEFAULT_ALLOWED_ATTRS

        entity = Entity({ **allowed_attrs, **UNKNOWN_ATTRS })

        for known_attr in allowed_attrs.keys():
            assert hasattr(entity, known_attr)
        for unknown_attr in UNKNOWN_ATTRS.keys():
            assert hasattr(entity, unknown_attr)

    def test_constructionValidatesForType(self, Entity, test_data):
        allowed_attrs = test_data.DEFAULT_ALLOWED_ATTRS
        wrong_attrs = test_data.WRONGTYPE_ATTRS
        
        for wrong_attr, value in wrong_attrs.items():
            args = allowed_attrs.copy()
            args.update({ wrong_attr: value })

            with pytest.raises(EntityValidationError):

                Entity(args)

    def test_constructionValidatesAttributeNotAllowingEmptyOrSpaces(self, Entity, test_data):
        allowed_attrs = test_data.DEFAULT_ALLOWED_ATTRS
        no_empty_spaces_attrs = test_data.ATTRS_NOT_WHITESPACE_OR_EMPTY
        wrong_strings = [
            '',
            ' ',
            '\t\t ',
        ]

        for wrong_string in wrong_strings:
            for attr in no_empty_spaces_attrs:
                attrs = allowed_attrs.copy()
                attrs[attr] = wrong_string

                with pytest.raises(EntityValidationError):

                    Entity(attrs)

    def test_constructionValidatesAttributeAllowingNone(self, Entity, test_data):
        allowed_attrs = test_data.DEFAULT_ALLOWED_ATTRS
        none_attrs = test_data.ATTRS_ALLOW_NONE
        
        for attr in none_attrs:
            attrs = {}
            attrs[attr] = None

            entity = Entity({ **allowed_attrs, **attrs })

            assert getattr(entity, attr) is None

    def test_constructionValidatesAttributesRestrictedValues(self, Entity, test_data):
        restricted_attributes = test_data.ATTRS_RESTRICTED_ATTRS

        for attr in restricted_attributes:
            for wrong_value in RANDOM_VALUES:
                args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
                args[ attr['name'] ] = wrong_value

                with pytest.raises(EntityValidationError):

                    Entity(args)

    def test_constructionAllowsAttributesRestrictedValues(self, Entity, test_data):
        restricted_attributes = test_data.ATTRS_RESTRICTED_ATTRS

        for allowed_attr in restricted_attributes:
            for allowed_val in allowed_attr['values']:
                args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
                args[ allowed_attr['name'] ] = allowed_val

                entity = Entity(args)

                assert getattr(entity, allowed_attr['name']) == allowed_val


@pytest.mark.parametrize(test_param_names, test_params, ids=test_types)
class TestConversionMethods:
    def create_entity(self, Entity, test_data):
        return Entity(test_data.DEFAULT_ALLOWED_ATTRS)

    def test_to_serializeConvertsEntityAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        entity_attrs = test_data.DEFAULT_ENTITY_ATTRS.keys()

        try:
            entity.to_serialize()
        except Exception:
            # ignore failed serialization during tests
            pass

        for attr in entity_attrs:
            attr_values = getattr(entity, attr)
        
            for attr_value in attr_values:
                assert attr_value._convert_dict_for.call_count == 1
                arg1, *_ = attr_value._convert_dict_for.call_args_list[0][0]
                assert arg1 == 'to_serialize'

    def test_to_serizlizeReturnsAttributeValues(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        entity_attrs = test_data.DEFAULT_ENTITY_ATTRS

        serialized = entity.to_serialize()

        for attr, value in serialized.items():
            if attr in entity_attrs:
                assert value == entity_attrs[attr]
            else:
                assert value == test_data.DEFAULT_ALLOWED_ATTRS[attr]

    def test_to_serializeIgnoresHiddenAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        hidden_attributes = test_data.TO_SERIALIZE_IGNORE_ATTRS

        serialized = entity.to_serialize()

        for attr in serialized.keys():
            assert attr not in hidden_attributes

    def test_to_serializeValidatesRequiredAttributes(self, Entity, test_data):
        required_attributes = test_data.TO_SERIALIZE_REQUIRED_ATTRS

        for required_attribute in required_attributes:
            args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
            args.pop(required_attribute)
            entity = Entity(args)

            with pytest.raises(EntityValidationError):

                entity.to_serialize()

    def test_to_serializeRaisesNoExceptionWhenMissinOptionalAttributes(self, Entity, test_data):
        optional_attributes = test_data.TO_SERIALIZE_OPTIONAL_ATTRS

        for optional_attribute in optional_attributes:
            args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
            args.pop(optional_attribute)
            entity = Entity(args)

            entity.to_serialize()

    def test_to_serializeCanOutputOptionalAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        optional_attributes = test_data.TO_SERIALIZE_OPTIONAL_ATTRS

        serialized = entity.to_serialize()
        
        for optional_attr in optional_attributes:
            assert optional_attr in serialized

    def test_to_serializeIgnoresUnknownAttributes(self, Entity, test_data):
        entity = Entity(test_data.DEFAULT_ALLOWED_ATTRS, **UNKNOWN_ATTRS)

        serialized = entity.to_serialize()

        for attr in UNKNOWN_ATTRS.keys():
            assert attr not in serialized

    def test_to_createIgnoresHiddenAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        hidden_attributes = test_data.TO_CREATE_IGNORE_ATTRS

        new_data = entity.to_create()

        for attr in new_data.keys():
            assert attr not in hidden_attributes

    def test_to_createValidatesRequiredAttributes(self, Entity, test_data):
        required_attributes = test_data.TO_CREATE_REQUIRED_ATTRS

        for required_attribute in required_attributes:
            args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
            args.pop(required_attribute)
            entity = Entity(args)

            with pytest.raises(EntityValidationError):

                entity.to_create()

    def test_to_createRaisesNoExceptionWhenMissinOptionalAttributes(self, Entity, test_data):
        optional_attributes = test_data.TO_CREATE_OPTIONAL_ATTRS

        for optional_attribute in optional_attributes:
            args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
            args.pop(optional_attribute)
            entity = Entity(args)

            entity.to_create()

    def test_to_createCanOutputOptionalAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        optional_attributes = test_data.TO_CREATE_OPTIONAL_ATTRS

        new_data = entity.to_create()
        
        for optional_attr in optional_attributes:
            assert optional_attr in new_data

    def test_to_createIgnoresUnknownAttributes(self, Entity, test_data):
        entity = Entity(test_data.DEFAULT_ALLOWED_ATTRS, **UNKNOWN_ATTRS)

        new_data = entity.to_create()

        for attr in UNKNOWN_ATTRS.keys():
            assert attr not in new_data

    def test_to_updateIgnoresHiddenAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        hidden_attributes = test_data.TO_UPDATE_IGNORE_ATTRS

        update_data = entity.to_update()

        for attr in update_data.keys():
            assert attr not in hidden_attributes

    def test_to_updateValidatesRequiredAttributes(self, Entity, test_data):
        required_attributes = test_data.TO_UPDATE_REQUIRED_ATTRS

        for required_attribute in required_attributes:
            args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
            args.pop(required_attribute)
            entity = Entity(args)

            with pytest.raises(EntityValidationError):

                entity.to_updatae()

    def test_to_updateRaisesNoExceptionWhenMissinOptionalAttributes(self, Entity, test_data):
        optional_attributes = test_data.TO_UPDATE_OPTIONAL_ATTRS

        for optional_attribute in optional_attributes:
            args = test_data.DEFAULT_ALLOWED_ATTRS.copy()
            args.pop(optional_attribute)
            entity = Entity(args)

            entity.to_update()

    def test_to_updateCanOutputOptionalAttributes(self, Entity, test_data):
        entity = self.create_entity(Entity, test_data)
        optional_attributes = test_data.TO_UPDATE_OPTIONAL_ATTRS

        update_data = entity.to_update()
        
        for optional_attr in optional_attributes:
            assert optional_attr in update_data

    def test_to_updateIgnoresUnknownAttributes(self, Entity, test_data):
        entity = Entity(test_data.DEFAULT_ALLOWED_ATTRS, **UNKNOWN_ATTRS)

        update_data = entity.to_update()

        for attr in UNKNOWN_ATTRS.keys():
            assert attr not in update_data
