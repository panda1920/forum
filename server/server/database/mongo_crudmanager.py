# -*- coding: utf-8 -*-
"""
This file houses the class MongoCrudManager.
It implements the CrudManager class to make CRUD operations to a mongoDB.
"""
import os

from pymongo import MongoClient

from server.database.crudmanager import CrudManager
from server.database.paging import Paging
from server.entity.user import NewUser, UpdateUser
import server.exceptions as exceptions

class MongoCrudManager(CrudManager):
    """
    Implements CrudManager interface to make CRUD operations
    to a mongoDB instance.
    """
    def __init__(self, dbname, userauth):
        hostname = os.getenv('MONGO_HOSTNAME')
        port = int( os.getenv('MONGO_PORT') )
        
        self._client = MongoClient(hostname, port)
        self._db = self._client[dbname]
        self._userauth = userauth

    def createUser(self, user):
        if not NewUser.validate(user):
            raise exceptions.EntityValidationError('failed to validate new user object')

        self._db['users'].insert_one( self._hashUserPassword(user) )

    def searchUser(self, searchFilters, paging = Paging()):
        if len(searchFilters) == 0:
            return []
        query = {
            '$and': [ searchFilter.getMongoFilter() for searchFilter in searchFilters ]
        }
        start = paging.offset
        end = None if paging.limit == None else start + paging.limit

        return list( self._db['users'].find(query)[start:end] )

    def deleteUser(self, userIds):
        query = { 'userId': {'$in': userIds} }
        self._db['users'].delete_many(query)

    def updateUser(self, user):
        if not UpdateUser.validate(user):
            raise exceptions.EntityValidationError('failed to validate update user object')

        query = { 'userId': { '$eq': user['userId'] } }
        update = { '$set': {} }
        hashedUser = self._hashUserPassword(user)
        for field in UpdateUser.getUpdatableFields():
            update['$set'][field] = hashedUser[field]
        
        result = self._db['users'].update_one(query, update)

        if result.matched_count == 0 or result.matched_count == 0:
            raise exceptions.RecordNotFoundError('failed to find the document to update')
    
    def createPost(self, post):
        pass
    
    def searchPost(self, searchFilters, paging = Paging()):
        pass

    def deletePost(self, postIds):
        pass

    def updatePost(self, post):
        pass

    def _hashUserPassword(self, user):
        copy = user.copy()
        copy['password'] = self._userauth.hashPassword( copy['password'] )
        return copy