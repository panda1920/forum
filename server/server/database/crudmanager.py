# -*- coding: utf-8 -*-
"""
This file houses the class CrudManager.
It is an interface to abstract away the detail of making CRUD operations.
"""


class CrudManager:
    def __init__(self):
        raise NotImplementedError

    def createUser(self, user):
        raise NotImplementedError

    def searchUser(self, searchFilter, paging=None):
        raise NotImplementedError

    def deleteUser(self, userIds):
        raise NotImplementedError

    def updateUser(self, seearchFilter, user):
        raise NotImplementedError
    
    def createPost(self, post):
        raise NotImplementedError
    
    def searchPost(self, searchFilter, paging=None):
        raise NotImplementedError

    def deletePost(self, postIds):
        raise NotImplementedError

    def updatePost(self, searchFilter, post):
        raise NotImplementedError
