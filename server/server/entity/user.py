# -*- coding: utf-8 -*-
"""
This file houses class that defines contextual user state
"""

import logging

from cerberus import Validator

from server.entity import Entity, extract_schema


class NewUser:
    """
    A namespace for new-user related operations
    """
    _schema = {
        'userId': {
            'type': 'string',
            'required': False,
        },
        'userName': {
            'type': 'string',
            'required': True,
            'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        },
        'displayName': {
            'type': 'string',
            'required': True,
        },
        'password': {
            'type': 'string',
            'required': True,
        },
        'createdAt': {
            'type': 'float',
            'required': False,
        },
        'imageUrl': {
            'type': 'string',
            'required': True,
        },
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newUser):
        return cls._validator.validate(newUser)


class UpdateUser:
    """
    A namespae for update-user related operations
    """
    _schema = {
        'password': {
            'type': 'string',
            'required': False,
        },
        'displayName': {
            'type': 'string',
            'required': False,
        },
        'imageUrl': {
            'type': 'string',
            'required': False,
        },
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, updateUser):
        return cls._validator.validate(updateUser)

    @classmethod
    def getUpdatableFields(cls):
        fields = [
            field for field in cls._schema.keys()
            if cls._schema[field]['required'] is False
        ]
        
        return fields


def removePrivateInfo(user):
    """
    removes sensitive information and implementation details from user
    intended to be called from services that return user information to client
    
    Args:
        user(dict): dict representing user entity
    Returns:
        dict: copy of arg user with fields removed
    """
    filtered_user = user.copy()
    filtered_user.pop('_id', None)
    filtered_user.pop('password', None)
    filtered_user.pop('address', None)

    return filtered_user


class User(Entity):
    """
    A class that defines User entity in the app
    """

    _attribute_description = {
        '_id': {
            'type': 'string',
            'to_json': {
                'required': False,
                'hide': True,
            },
            'to_create': {
                'required': False,
                'hide': True,
            },
            'to_update': {
                'required': False,
                'hide': True,
            },
        },
        'userId': {
            'type': 'string',
            'to_json': {
                'required': False,
                'hide': False,
            },
            'to_create': {
                'required': True,
                'hide': False,
            },
            'to_update': {
                'required': False,
                'hide': True,
            },
        },
        'userName': {
            'type': 'string',
            'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            'to_json': {
                'required': False,
                'hide': True,
            },
            'to_create': {
                'required': True,
                'hide': False,
            },
            'to_update': {
                'required': False,
                'hide': True,
            },
        },
        'displayName': {
            'type': 'string',
            'to_json': {
                'required': False,
                'hide': False,
            },
            'to_create': {
                'required': True,
                'hide': False,
            },
            'to_update': {
                'required': False,
                'hide': False,
            },
        },
        'password': {
            'type': 'string',
            'to_json': {
                'required': False,
                'hide': True,
            },
            'to_create': {
                'required': True,
                'hide': False,
            },
            'to_update': {
                'required': False,
                'hide': False,
            },
        },
        'updatedAt': {
            'type': 'float',
            'to_json': {
                'required': False,
                'hide': False,
            },
            'to_create': {
                'required': False,
                'hide': True,
            },
            'to_update': {
                'required': False,
                'hide': True,
            },
        },
        'createdAt': {
            'type': 'float',
            'to_json': {
                'required': False,
                'hide': False,
            },
            'to_create': {
                'required': False,
                'hide': True,
            },
            'to_update': {
                'required': False,
                'hide': True,
            },
        },
        'imageUrl': {
            'type': 'string',
            'to_json': {
                'required': False,
                'hide': False,
            },
            'to_create': {
                'required': False,
                'hide': False,
            },
            'to_update': {
                'required': False,
                'hide': False,
            },
        },
    }
    _schema = extract_schema(_attribute_description)
    _validator = Validator(_schema, purge_unknown=True)
    _logger = logging.getLogger(__name__)
