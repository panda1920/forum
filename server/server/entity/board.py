# -*- coding: utf-8 -*-
"""
This file houses Board entity
"""
import logging

from server.entity import Entity, extract_schema

from cerberus import Validator


class Board(Entity):
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
        'boardId': {
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
        'title': {
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
            }
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
                    'hide': False,
                },
            },
        },
    }
    _schema = extract_schema(_attribute_description)
    _validator = Validator(_schema, allow_unknown=True)
    _logger = logging.getLogger(__name__)
