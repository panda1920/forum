# -*- coding: utf-8 -*-
"""
This file defines entity thread
"""
from cerberus import Validator


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
