# -*- coding: utf-8 -*-
"""
This file houses class that serves the app with auth related methods
"""

import logging

from passlib.context import CryptContext

import server.exceptions as exceptions


class PasswordService:
    """
    namepace to put all password related methods
    """
    # context file used to hash/verify passwords
    _context = CryptContext(
        schemes=['pbkdf2_sha256'],
        deprecated='auto'
    )

    @classmethod
    def hashPassword(cls, password):
        """
        Hashes password to be stored in database
        
        Args:
            password(str): password to hash
        Returns:
            str: hashed password
        """
        return cls._context.hash(password)

    @classmethod
    def verifyPassword(cls, password, hash):
        """
        verify password so that it matches hash
        
        Args:
            password(str): plain text password to verify
            hash(str): hashed password that plain password is matched against
        Returns:
            boolean: whether verification succeeded or not
        """
        try:
            return cls._context.verify(password, hash)
        except Exception:
            # hash generated by different context raises exception
            return False


class UserAuthenticationService:
    """
    Class that provides login/logout functionality to the app.
    Houses business logic related to such authentication process.
    """
    def __init__(self, repo, filter_class, session_manager):
        self._repo = repo
        self._filter = filter_class
        self._session = session_manager

    def login(self, credential):
        """
        provides login service
        checks credential against user in repo,
        and if matches put userinformation in session
        
        Args:
            credential(dict): dictionary that contains user credential
        Returns:
            None
        """
        userName, password = self._extractUserNameAndPassword(credential)
        user_indb = self._searchUserFromRepo(userName)

        if not PasswordService.verifyPassword(password, user_indb['password']):
            logging.info('Failed to verify password')
            raise exceptions.InvalidUserCredentials('Incorrect password')

        self._session.set_user(user_indb)

    def _extractUserNameAndPassword(self, credential):
        userName = credential.get('userName', None)
        password = credential.get('password', None)

        if not userName or not password:
            logging.info('Invalid user credential')
            raise exceptions.InvalidUserCredentials('Invalid credential')

        return (userName, password)

    def _searchUserFromRepo(self, userName):
        searchFilter = self._filter.createFilter(dict(
            field='userName', operator='eq', value=[userName]
        ))
        
        result = self._repo.searchUser(searchFilter)
        try:
            return result['users'][0]
        except Exception as e:
            logging.error(e)
            raise exceptions.InvalidUserCredentials('Email not registered')

    def logout(self):
        """
        provides logout service
        
        Args:
            None
        Returns:
            None
        """
        self._session.remove_user()
