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
from server.entity.post import NewPost, UpdatePost
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
        self._validateEntity(NewUser, user)

        self._db['users'].insert_one( self._hashUserPassword(user) )

    def searchUser(self, searchFilters, paging = Paging()):
        # if len(searchFilters) == 0:
        #     return []
        query = {}
        if len(searchFilters) > 0:
            query = self._combineSearchFilterAnd(searchFilters)
        start = paging.offset
        end = None if paging.limit == None else start + paging.limit

        return list( self._db['users'].find(query)[start:end] )

    def deleteUser(self, userIds):
        userQuery = { 'userId': { '$in': userIds } }
        postQuery = userQuery

        self._db['users'].delete_many(userQuery)
        self._db['posts'].delete_many(postQuery)

    def updateUser(self, user):
        self._validateEntity(UpdateUser, user)
        query = { 'userId': { '$eq': user['userId'] } }
        passwordHashedUser = self._hashUserPassword(user)
        update = self._createMongoUpdate(UpdateUser, passwordHashedUser)
        
        result = self._db['users'].update_one(query, update)
        if result.matched_count == 0:
            raise exceptions.RecordNotFoundError('failed to find document')
        if result.modified_count == 0:
            raise exceptions.FailedMongoOperation('failed to update document')
    
    def createPost(self, post):
        self._validateEntity(NewPost, post)
        
        result = self._db['posts'].insert_one(post)
    
    def searchPost(self, searchFilters, paging = Paging()):
        if len(searchFilters) == 0:
            return []
        query = self._combineSearchFilterAnd(searchFilters)
        start = paging.offset
        end = None if paging.limit == None else start + paging.limit

        return list( self._db['posts'].find(query)[start:end] )

    def deletePost(self, postIds):
        query = { 'postId': { '$in': postIds } }

        result = self._db['posts'].delete_many(query)

    def updatePost(self, post):
        self._validateEntity(UpdatePost, post)
        query = { 'postId': { '$eq' : post['postId'] } }
        update = self._createMongoUpdate(UpdatePost, post)

        result = self._db['posts'].update_one(query, update)
        if result.matched_count == 0:
            raise exceptions.RecordNotFoundError('failed to find document')
        if result.modified_count == 0:
            raise exceptions.FailedMongoOperation('failed to update document')

    def _hashUserPassword(self, user):
        copy = user.copy()
        copy['password'] = self._userauth.hashPassword( copy['password'] )
        return copy

    def _createMongoUpdate(self, entitySchema, updateProps):
        update = { '$set': {} }
        for field in entitySchema.getUpdatableFields():
            update['$set'][field] = updateProps[field]
        return update

    def _combineSearchFilterAnd(self, searchFilters):
        return {
            '$and': [ searchFilter.getMongoFilter() for searchFilter in searchFilters ]
        }

    def _validateEntity(self, entitySchema, entity):
        if not entitySchema.validate(entity):
            raise exceptions.EntityValidationError(f'failed to validate {entitySchema.__name__}')