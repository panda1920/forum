# -*- coding: utf-8 -*-
"""
This file houses service to access the flask context
"""

import logging

from flask import g, session

logger = logging.getLogger(__name__)


class FlaskContext:
    """
    Class that provides interface to flask context
    The motivation to create this class was to make testing easier
    Other classes that need to access flask context can use this class,
    and during tests it can be mocked out to promote decoupled development
    """

    def write_global(self, key, value):
        """
        Writes the key and value to flask.g

        Args:
            key(string): key to reference the value upon retrieval
            value: anything
        Returns:
            None
        """
        logger.info('Writing value to global context')
        logger.debug('with key %s', key)
        setattr(g, key, value)

    def read_global(self, key):
        """
        Reads from flask.g
        
        Args:
            key(string)
        Returns:
            return value that corresponds to key
        """
        logger.info('Reading value from global context')
        logger.debug('with key %s', key)
        value = g.get(key, None)
        if value is None:
            logger.warning(f'Key {key} not found in flask.g')

        return value
    
    def delete_global(self, key):
        """
        Deletes key from global
        
        Args:
            key(string)
        Returns:
            None
        """
        logger.info('Deleting value from global context')
        logger.debug('with key %s', key)
        try:
            g.pop(key)
        except Exception:
            logger.warning(f'Key {key} not found in flask.g')

    def write_session(self, key, value):
        """
        Writes the key and value to flask.session

        Args:
            key(string): key to reference the value upon retrieval
            value: anything
        Returns:
            None
        """
        logger.info('Writing value to flask.session')
        logger.debug('with key %s', key)
        session[key] = value
        session.modified = True

    def read_session(self, key):
        """
        Reads from flask.session
        
        Args:
            key(string)
        Returns:
            return value that corresponds to key
        """
        logger.info('Reading value from flask.session')
        logger.debug('with key %s', key)
        value = session.get(key, None)
        if value is None:
            logger.warning(f'Key {key} not found in flask.session')

        return value
    
    def delete_session(self, key):
        """
        Deletes key from flask.session
        
        Args:
            key(string)
        Returns:
            None
        """
        logger.info('Deleting value from flask.session')
        logger.debug('with key %s', key)
        try:
            session.pop(key)
        except Exception:
            logger.warning(f'Key {key} not found in flask.session')
