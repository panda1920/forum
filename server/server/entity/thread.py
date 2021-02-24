# -*- coding: utf-8 -*-
"""
This file defines entity thread
"""
import logging

from cerberus import Validator, TypeDefinition

from server.entity import Entity, extract_schema


class Thread(Entity):
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
        'threadId': {
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
                    'required': True,
                    'hide': False,
                },
                'to_update': {
                    'required': False,
                    'hide': True,
                },
            },
        },
        'lastPostId': {
            'validation_rules': {
                'type': 'string',
                'nullable': True,
            },
            'conversion_rules': {
                'to_serialize': {
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
        },
        'owner': {
            'validation_rules': {
                'type': 'list'
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
        'ownerBoard': {
            'validation_rules': {
                'type': 'list'
            },
            'conversion_rules': {
                'to_serialize': {
                    'required': False,
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
        'lastPost': {
            'validation_rules': {
                'type': 'list'
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
                'regex': r'.*\S+.*',
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
        'subject': {
            'validation_rules': {
                'type': 'string',
                'regex': r'.*\S+.*',
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
        'views': {
            'validation_rules': {
                'type': 'integer',
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
        },
        'postCount': {
            'validation_rules': {
                'type': 'integer',
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
        },
        'increment': {
            'validation_rules': {
                'type': 'string',
                'allowed': ['views', 'postCount']
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
                    'hide': False,
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
    }
    _schema = extract_schema(_attribute_description)
    _validator = Validator(_schema, allow_unknown=True)
    _logger = logging.getLogger(__name__)


# adds custom type checking for validator
thread_type = TypeDefinition('Thread', (Thread,), ())
Validator.types_mapping['Thread'] = thread_type
