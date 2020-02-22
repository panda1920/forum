# -*- coding: utf-8 -*-
"""
This file houses the class MongoCrudManager.
It implements the CrudManager class to make CRUD operations to a mongoDB.
"""
import os

from pymongo import MongoClient
from contextlib import contextmanager

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
        user['password'] = self._userauth.hashPassword( user['password'] )

        with self._mongoOperationHandling('Failed to create user'):
            nextUserId = self._getCounterAndIncrement('userId')
            user['userId'] = str(nextUserId)
            self._db['users'].insert_one(user)

    def searchUser(self, searchFilter, paging=Paging()):
        query = {} if searchFilter is None else searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to search user'):
            users = list(paging.slice( self._db['users'].find(query) ))
            matchedCount = self._db['users'].count_documents(query)
            
        return {
            'users': users,
            'returnCount': len(users),
            'matchedCount': matchedCount,
        }

    def deleteUser(self, userIds):
        userQuery = { 'userId': { '$in': userIds } }
        postQuery = userQuery

        with self._mongoOperationHandling('Failed to delete user'):
            self._db['users'].delete_many(userQuery)
            self._db['posts'].delete_many(postQuery)

    def updateUser(self, searchFilter, user):
        self._validateEntity(UpdateUser, user)
        user['password'] = self._userauth.hashPassword( user['password'] )
        query = searchFilter.getMongoFilter()
        update = self._createMongoUpdate(UpdateUser, user)
        
        with self._mongoOperationHandling('Failed to update user'):
            result = self._db['users'].update_many(query, update)

        return dict(
            matchedCount=result.matched_count,
            updatedCount=result.modified_count,
        )
    
    def createPost(self, post):
        self._validateEntity(NewPost, post)
        
        with self._mongoOperationHandling('Failed to create post'):
            nextPostId = self._getCounterAndIncrement('postId')
            post['postId'] = str(nextPostId)
            self._db['posts'].insert_one(post)
    
    def searchPost(self, searchFilter, paging=Paging()):
        query = {} if searchFilter is None else searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to search post'):
            posts = list(paging.slice( self._db['posts'].find(query) ))
            matchedCount = self._db['posts'].count_documents(query)

        return {
            'posts': posts,
            'returnCount': len(posts),
            'matchedCount': matchedCount,
        }

    def deletePost(self, postIds):
        query = { 'postId': { '$in': postIds } }

        with self._mongoOperationHandling('Failed to create post'):
            self._db['posts'].delete_many(query)

    def updatePost(self, searchFilter, post):
        self._validateEntity(UpdatePost, post)
        query = searchFilter.getMongoFilter()
        update = self._createMongoUpdate(UpdatePost, post)

        with self._mongoOperationHandling('Failed to create post'):
            result = self._db['posts'].update_many(query, update)

        return dict(
            matchedCount=result.matched_count,
            updatedCount=result.modified_count,
        )

    def _createMongoUpdate(self, entitySchema, updateProps):
        update = { '$set': {} }
        for field in entitySchema.getUpdatableFields():
            update['$set'][field] = updateProps[field]
        return update

    def _validateEntity(self, entitySchema, entity):
        if not entitySchema.validate(entity):
            raise exceptions.EntityValidationError(f'failed to validate {entitySchema.__name__}')

    def _createCounterQuery(self, fieldname):
        return dict(
            fieldname={ '$eq': fieldname }
        )

    def _getCounterAndIncrement(self, fieldname):
        counterQuery = self._createCounterQuery(fieldname)
        counterValue = self._db['counters'].find_one(counterQuery)['value']
        update = { '$inc': { 'value': 1 } }
        self._db['counters'].update_one(counterQuery, update)

        return counterValue

    @contextmanager
    def _mongoOperationHandling(self, errormsg):
        try:
            yield
        except Exception as e:
            print(e)
            raise exceptions.FailedMongoOperation(errormsg)
