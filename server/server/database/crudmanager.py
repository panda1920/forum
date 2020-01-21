# -*- coding: utf-8 -*-
"""
This file houses the class CrudManager.
It is an interface to abstract away the detail of making CRUD operations.
"""

from server.database.paging import Paging

class CrudManager:
    def __init__(self):
        raise NotImplementedError

    def createUser(self, user):
        raise NotImplementedError

    def searchUser(self, searchFilters, paging = Paging()):
        raise NotImplementedError

    def deleteUser(self, userIds):
        raise NotImplementedError

    def updateUser(self, user):
        raise NotImplementedError
    
    def createPost(self, post):
        raise NotImplementedError
    
    def searchPost(self, searchFilters, paging = Paging()):
        raise NotImplementedError

    def deletePost(self, postIds):
        raise NotImplementedError

    def updatePost(self, post):
        raise NotImplementedError