# -*- coding: utf-8 -*-
"""
This file houses Base Entity class
"""

import json

from server.exceptions import EntityValidationError


class Entity:
    """
    Entity class that defines operations common to all entities in this app
    """

    def __init__(self, object=None, **kwargs):
        self._sanitize_attributes(object, **kwargs)

    def to_json(self):
        attrs = self._prepare_attributes('to_json')

        return json.dumps(attrs)

    def to_create(self):
        return self._prepare_attributes('to_create')

    def to_update(self):
        return self._prepare_attributes('to_update')

    def _sanitize_attributes(self, object, **kwargs):
        to_add = {}
        if object:
            to_add.update(object)
        to_add.update(kwargs)
        normalized = self._validator.normalized(to_add)

        if not self._validator.validate(normalized):
            self._logger.error('Failed validation in %s creation', self.__class__.__name__)
            for attr, reason in self._validator.errors.items():
                self._logger.error('{ attribute: %s,  reason: %s }', attr, reason)

            raise EntityValidationError(f'Failed to validate {self.__class__.__name__}')
        
        self.__dict__.update(normalized)

    def _prepare_attributes(self, operation):
        attrs = self.__dict__.copy()
        required_attrs = [
            attr for attr in self._attribute_description.keys()
            if self._attribute_description[attr][operation]['required']
        ]
        hidden_attrs = [
            attr for attr in self._attribute_description.keys()
            if self._attribute_description[attr][operation]['hide']
        ]

        for attr in required_attrs:
            if attr not in attrs:
                self._logger.error('Failed validation in %s', operation)
                raise EntityValidationError(f'Failed to validate {self.__class__.__name__}')
        for attr in hidden_attrs:
            attrs.pop(attr, None)

        return attrs


def extract_schema(attribute_description):
    """
    Helper function to extract a valid cerberus schema
    
    Args:
        attribute_description(dict): predefined description of allowed attributes defined in entity
    Returns:
        a valid cerberus schema
    """
    non_rules = [
        'to_json',
        'to_create',
        'to_update',
    ]
    schema = {}

    for attr_name, attr in attribute_description.items():
        schema[attr_name] = {}

        for rule_name, rule in attr.items():
            if rule_name not in non_rules:
                schema[attr_name][rule_name] = rule

    return schema
