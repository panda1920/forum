# -*- coding: utf-8 -*-
"""
This file houses buisness logic related to user signup
"""

from flask import current_app

import server.exceptions as exceptions
import server.app_utils as app_utils

class Signup:
    @staticmethod
    def signup(userProps):
        db = app_utils.getDB(current_app)

        if Signup.userExists(userProps, db):
            raise exceptions.DuplicateUserError('Username already used')
        
        Signup.createUser(userProps, db)

    @staticmethod
    def userExists(userProps, db):
        searchFilters = [
            app_utils.getFilter(current_app).createFilter({
                'field': 'userName',
                'operator': 'eq',
                'value': [ userProps['userName'] ],
            })
        ]
        users = db.searchUser(searchFilters)

        return len(users) > 0

    @staticmethod
    def createUser(userProps, db):
        atIdx = userProps['userName'].find('@')
        defaultName = userProps['userName'][:atIdx]

        db.createUser({
            **userProps,
            'displayName': defaultName,
        })