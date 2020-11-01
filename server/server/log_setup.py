# -*- coding: utf-8 -*-
"""
This file houses setup function for logger used around the app
"""
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
from pathlib import Path


def setup():
    logger = logging.getLogger( os.getenv('ROOT_MODULE_NAME') )
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    handler = create_loghandler()
    formatter = create_formatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def create_loghandler():
    """
    Creates a handler based on IS_PROD environment variable.
    For development, handler simply dumps log to stdout.
    For produciton, handler spits out log to a file.
    The file is rotated everyday at midnight.
    
    Args:
        arguments
    Returns:
        return value
    """
    is_test = os.getenv('IS_PROD', 'False') != 'True'
    if is_test:
        return logging.StreamHandler(sys.stdout)

    filepath = Path(
        os.getenv('LOG_OUTPUT_LOCATION'),
        os.getenv('LOG_FILENAME')
    )
    backup_count = int( os.getenv('BACKUP_COUNT', '7') )
    handler = TimedRotatingFileHandler(
        filepath,
        when='midnight',
        backupCount=backup_count,
    )

    return handler


def create_formatter():
    return logging.Formatter(
        '%(levelname)s %(asctime)s %(name)s:%(lineno)s -- %(message)s'
    )
