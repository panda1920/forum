# -*- coding: utf-8 -*-
"""
This file houses class that defines contextual user state
"""

import logging

from cerberus import Validator, TypeDefinition

from server.entity import Entity, extract_schema


class User(Entity):
    """
    A class that defines User entity in the app
    """

    _attribute_description = {
        '_id': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_serialize': {
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
        },
        'userId': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': True,
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
        },
        'userName': {
            'validation_rules': {
                'type': 'string',
                'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': True,
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
            'search_rules': {
                'fuzzy': True,
            },
        },
        'displayName': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': True,
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
            'search_rules': {
                'fuzzy': True,
            },
        },
        'password': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_serialize': {
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
        },
        'updatedAt': {
            'validation_rules': {
                'type': 'float',
            },
            'conversion_rules': {
                'to_serialize': {
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
        },
        'createdAt': {
            'validation_rules': {
                'type': 'float',
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': True,
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
        },
        'imageUrl': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': True,
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
        },
    }
    _schema = extract_schema(_attribute_description)
    _validator = Validator(_schema, purge_unknown=True)
    _logger = logging.getLogger(__name__)


# adds custom type checking for validator
user_type = TypeDefinition('User', (User,), ())
Validator.types_mapping['User'] = user_type
