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

    def searchUser(self, searchFilter, **options):
        raise NotImplementedError

    def deleteUser(self, userIds):
        raise NotImplementedError

    def updateUser(self, seearchFilter, user):
        raise NotImplementedError
    
    def createPost(self, post):
        raise NotImplementedError
    
    def searchPost(self, searchFilter, **options):
        raise NotImplementedError

    def deletePost(self, searchFilter):
        raise NotImplementedError

    def updatePost(self, searchFilter, post):
        raise NotImplementedError

    def createThread(self, thread):
        raise NotImplementedError

    def searchThread(self, searchFilter, **options):
        raise NotImplementedError

    def updateThread(self, searchFilter, thread):
        raise NotImplementedError

    def deleteThread(self, searchFilter):
        raise NotImplementedError
