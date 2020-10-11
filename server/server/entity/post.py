# -*- coding: utf-8 -*-
"""
This file houses classes that define contextual user state
"""
import logging

from cerberus import Validator, TypeDefinition

from server.entity import Entity, extract_schema


class NewPost:
    """
    A namespace for new-post related operations
    """
    _schema = {
        'userId': {
            'type': 'string',
            'required': True,
        },
        'content': {
            'type': 'string',
            'required': True,
        },
        'postId': {
            'type': 'string',
            'required': False,
        },
        'createdAt': {
            'type': 'float',
            'required': False,
        }
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newPost):
        return cls._validator.validate(newPost)

    @classmethod
    def getFields(cls):
        return cls._schema.keys()


class UpdatePost:
    """
    A namespace for update-post related operations
    """
    _schema = {
        'content': {
            'type': 'string',
            'required': False,
        },
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, updatePost):
        return cls._validator.validate(updatePost)

    @classmethod
    def getUpdatableFields(cls):
        fields = [
            field for field in cls._schema.keys()
            if cls._schema[field]['required'] is False
        ]
        
        return fields


def removePrivateInfo(post):
    """
    removes sensitive information and implementation details from post
    intended to be called from services that return post information to client
    
    Args:
        post(dict): dict representing post entity
    Returns:
        dict: copy of arg post with fields removed
    """
    filtered_post = post.copy()
    filtered_post.pop('_id', None)

    return filtered_post


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
        'postId': {
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
        'content': {
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
                    'hide': False,
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
    }
    _schema = extract_schema(_attribute_description)
    _validator = Validator(_schema, purge_unknown=True)
    _logger = logging.getLogger(__name__)


# adds custom type checking for validator
post_type = TypeDefinition('Post', (Post,), ())
Validator.types_mapping['Post'] = post_type
