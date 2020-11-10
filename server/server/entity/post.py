# -*- coding: utf-8 -*-
"""
This file houses classes that define contextual user state
"""
import logging

from cerberus import Validator, TypeDefinition

from server.entity import Entity, extract_schema


class Post(Entity):
    """
    A class that defines Post entity in the app.
    Represents all data related to a single post made on forum.
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
                    'required': True,
                    'hide': False,
                },
                'to_update': {
                    'required': False,
                    'hide': True,
                },
            },
        },
        'postId': {
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
        'content': {
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
                'fuzzy': True
            },
        },
        'owner': {
            'validation_rules': {
                'type': 'list',
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': True,
                    'hide': False,
                    'entity': True,
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
    }
    _schema = extract_schema(_attribute_description)
    _validator = Validator(_schema, purge_unknown=True)
    _logger = logging.getLogger(__name__)


# adds custom type checking for validator
post_type = TypeDefinition('Post', (Post,), ())
Validator.types_mapping['Post'] = post_type
