# -*- coding: utf-8 -*-
"""
This file houses Base Entity class
"""

import json

from server.exceptions import EntityValidationError


class Entity:
    """
    Base class that defines operations common to all entities in this app
    """

    def __init__(self, object=None, **kwargs):
        self._sanitize_attributes(object, **kwargs)

    def to_json(self):
        """
        Creates a JSON representation of this entity
        
        Args:
            None
        Returns:
            JSON string
        """
        attrs = self._prepare_attributes('to_json')

        return json.dumps(attrs)

    def to_create(self):
        """
        Creates a dictionary of attributes that represents this entity.
        Intended to be used in creation operation to persistent storage.
        
        Args:
            None
        Returns:
            Dict of attributes
        """
        return self._prepare_attributes('to_create')

    def to_update(self):
        """
        Creates a dictionary of attributes that represents this entity.
        Intended to be used in update operation to persistent storage.
        
        Args:
            None
        Returns:
            Dict of attributes
        """
        return self._prepare_attributes('to_update')

    def _sanitize_attributes(self, object, **kwargs):
        """
        Add constructor arguments as self's attribute.
        Additionally perform typecheck and removal of unexpected attributes.
        """

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
        """
        Creates a dictionary suited for the specified operation.
        Removes what needes to be hidden,
        validates that attributes meets requirements of the operation.
        
        Args:
            operatin(string): 'to_json'|'to_create'|'to_update'
        Returns:
            dictionary of attributes
        """
        attrs = self.__dict__.copy()
        print(self._attribute_description)
        required_attrs = [
            attr for attr in self._attribute_description.keys()
            if self._attribute_description[attr]['conversion_rules'][operation]['required']
        ]
        hidden_attrs = [
            attr for attr in self._attribute_description.keys()
            if self._attribute_description[attr]['conversion_rules'][operation]['hide']
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
        attribute_description(dict): description of allowed attributes predefined in concrete entity class
    Returns:
        a valid cerberus schema
    """
    schema = {}

    for attr_name, attr in attribute_description.items():
        schema[attr_name] = attr['validation_rules']

    return schema
