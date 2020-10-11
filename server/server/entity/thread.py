# -*- coding: utf-8 -*-
"""
This file defines entity thread
"""
import logging

from cerberus import Validator, TypeDefinition

from server.entity import Entity, extract_schema


class NewThread:
    """
    This class defines thread entity in its creation phase.
    """
    _schema = {
        'boardId': {
            'type': 'string',
            'required': True,
        },
        'userId': {
            'type': 'string',
            'required': True,
        },
        'title': {
            'type': 'string',
            'required': True,
            'regex': r'\s*\S+\s*',
        },
        'subject': {
            'type': 'string',
            'required': True,
            'regex': r'\s*\S+\s*',
        },
        'threadId': {
            'type': 'string',
            'required': False,
        },
        'createdAt': {
            'type': 'float',
            'required': False,
        },
        'views': {
            'type': 'integer',
            'required': False,
        },
    }

    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newThread):
        return cls._validator.validate(newThread)

    @classmethod
    def getFields(cls):
        return cls._schema.keys()


class UpdateThread:
    """
    This class defines object to update thread entities.
    """
    _schema = {
        'userId': {
            'type': 'string',
            'required': False,
        },
        'title': {
            'type': 'string',
            'required': False,
            'regex': r'\s*\S+\s*',
        },
        'subject': {
            'type': 'string',
            'required': False,
            'regex': r'\s*\S+\s*',
        },
        'views': {
            'type': 'integer',
            'required': False,
        },
        'increment': {
            'type': 'string',
            'allowed': [ 'views' ],
            'required': False,
        },
    }

    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, updateThread):
        return cls._validator.validate(updateThread)

    @classmethod
    def getUpdatableFields(cls):
        fields = [
            field for field in cls._schema.keys()
            if cls._schema[field] != 'increment'
        ]
        
        return fields


def removePrivateInfo(thread):
    """
    removes sensitive information and implementation details from thread
    intended to be called from services that return thread information to client
    
    Args:
        thread(dict): dict representing thread entity
    Returns:
        dict: copy of arg thread with fields removed
    """
    filtered_thread = thread.copy()
    filtered_thread.pop('_id', None)

    return filtered_thread


class Thread(Entity):
    _attribute_description = {
        '_id': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
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
        },
        'threadId': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_json': {
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
                'to_json': {
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
        'boardId': {
            'validation_rules': {
                'type': 'string',
            },
            'conversion_rules': {
                'to_json': {
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
        'title': {
            'validation_rules': {
                'type': 'string',
                'regex': r'\s*\S+\s*',
            },
            'conversion_rules': {
                'to_json': {
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
        'subject': {
            'validation_rules': {
                'type': 'string',
                'regex': r'\s*\S+\s*',
            },
            'conversion_rules': {
                'to_json': {
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
        'views': {
            'validation_rules': {
                'type': 'integer',
            },
            'conversion_rules': {
                'to_json': {
                    'required': True,
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
        'increment': {
            'validation_rules': {
                'type': 'string',
                'allowed': ['views']
            },
            'conversion_rules': {
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
                    'hide': False,
                },
            },
        },
        'createdAt': {
            'validation_rules': {
                'type': 'float',
            },
            'conversion_rules': {
                'to_json': {
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
                'to_json': {
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
thread_type = TypeDefinition('Thread', (Thread,), ())
Validator.types_mapping['Thread'] = thread_type
