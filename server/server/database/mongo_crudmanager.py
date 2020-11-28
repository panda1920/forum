# -*- coding: utf-8 -*-
"""
This file houses the class MongoCrudManager.
It implements the CrudManager class to make CRUD operations to a mongoDB.
"""
import os
import time
import logging
from collections import defaultdict

from pymongo import MongoClient
from contextlib import contextmanager

from server.database.sorter import NullSorter
from server.database.crudmanager import CrudManager
from server.database.paging import Paging
import server.exceptions as exceptions
from server.entity import User, Post, Thread, Board


logger = logging.getLogger(__name__)


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
        attrs = user.to_create()
        attrs['password'] = self._userauth.hashPassword( attrs['password'] )

        with self._mongoOperationHandling('Failed to create attrs'):
            nextUserId = str( self._getCounterAndIncrement('userId') )
            attrs['userId'] = nextUserId
            attrs['createdAt'] = time.time()
            self._db['users'].insert_one(attrs)

        return dict(
            createdCount=1,
            createdId=nextUserId
        )

    def searchUser(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')
        query = {} if searchFilter is None else searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to search user'):
            users = list( paging.slice( sorter.sortMongoCursor( self._db['users'].find(query) ) ) )
            matchedCount = self._db['users'].count_documents(query)
            
        # convert dictionary to User object
        self._convertInnerIdToStr(users)
        users = [ User(user) for user in users ]

        return {
            'users': users,
            'returnCount': len(users),
            'matchedCount': matchedCount,
        }

    def deleteUser(self, searchFilter):
        userQuery = searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to delete user'):
            result = self._db['users'].delete_many(userQuery)

        return dict(deleteCount=result.deleted_count)

    def updateUser(self, searchFilter, user):
        attrs = user.to_update()
        attrs['password'] = self._userauth.hashPassword( attrs['password'] )
        query = searchFilter.getMongoFilter()
        update = self._createMongoUpdate(attrs)
        
        with self._mongoOperationHandling('Failed to update attrs'):
            result = self._db['users'].update_many(query, update)

        return dict(
            matchedCount=result.matched_count,
            updatedCount=result.modified_count,
        )
    
    def createPost(self, post):
        attrs = post.to_create()
        
        with self._mongoOperationHandling('Failed to create post'):
            nextPostId = str( self._getCounterAndIncrement('postId') )
            attrs['postId'] = nextPostId
            attrs['createdAt'] = time.time()
            self._db['posts'].insert_one(attrs)

        return dict(
            createdCount=1,
            createdId=nextPostId,
        )
    
    def searchPost(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')
        query = {} if searchFilter is None else searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to search post'):
            posts = list( paging.slice( sorter.sortMongoCursor( self._db['posts'].find(query) ) ) )
            matchedCount = self._db['posts'].count_documents(query)

        self._convertInnerIdToStr(posts)
        posts = [ Post(post) for post in posts ]

        return {
            'posts': posts,
            'returnCount': len(posts),
            'matchedCount': matchedCount,
        }

    def deletePost(self, searchFilter):
        query = searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to create post'):
            result = self._db['posts'].delete_many(query)

        return dict(deleteCount=result.deleted_count)

    def updatePost(self, searchFilter, post):
        attrs = post.to_update()
        query = searchFilter.getMongoFilter()
        update = self._createMongoUpdate(attrs)

        with self._mongoOperationHandling('Failed to update post'):
            result = self._db['posts'].update_many(query, update)

        return dict(
            matchedCount=result.matched_count,
            updatedCount=result.modified_count,
        )

    def createThread(self, thread):
        attrs = thread.to_create()

        with self._mongoOperationHandling('Failed to create new thread'):
            nextThreadId = str( self._getCounterAndIncrement('threadId') )
            attrs['threadId'] = nextThreadId
            attrs['createdAt'] = time.time()
            self._db['threads'].insert_one(attrs)

        return dict(
            createdCount=1,
            createdId=nextThreadId,
        )

    def searchThread(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')
        query = {} if searchFilter is None else searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to search for threads'):
            threads = list( paging.slice( sorter.sortMongoCursor( self._db['threads'].find(query) ) ) )
            matchedCount = self._db['threads'].count_documents(query)

        self._convertInnerIdToStr(threads)
        threads = [ Thread(thread) for thread in threads ]

        return dict(
            threads=threads,
            matchedCount=matchedCount,
            returnCount=len(threads),
        )

    def updateThread(self, searchFilter, thread):
        attrs = thread.to_update()

        fil = searchFilter.getMongoFilter()
        update = self._createMongoUpdate(attrs)
        with self._mongoOperationHandling('Failed to update thread'):
            result = self._db['threads'].update_many(fil, update)

        return dict(
            matchedCount=result.matched_count,
            updatedCount=result.modified_count,
        )

    def deleteThread(self, searchFilter):
        query = searchFilter.getMongoFilter()
        with self._mongoOperationHandling('Failed to delete thread'):
            result = self._db['threads'].delete_many(query)

        return dict(
            deleteCount=result.deleted_count,
        )

    def createBoard(self, board):
        attrs = board.to_create()

        with self._mongoOperationHandling('Failed to create new thread'):
            nextId = str( self._getCounterAndIncrement('boardId') )
            attrs['boardId'] = nextId
            attrs['createdAt'] = time.time()
            self._db['boards'].insert_one(attrs)

        return dict(
            createdCount=1,
            createdId=nextId,
        )

    def searchBoard(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')
        query = {} if searchFilter is None else searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to search board'):
            boards = list( paging.slice( sorter.sortMongoCursor( self._db['boards'].find(query) ) ) )
            matchedCount = self._db['boards'].count_documents(query)

        self._convertInnerIdToStr(boards)
        boards = [ Board(board) for board in boards ]

        return {
            'boards': boards,
            'returnCount': len(boards),
            'matchedCount': matchedCount,
        }

    def updateBoard(self, searchFilter, board):
        attrs = board.to_update()

        fil = searchFilter.getMongoFilter()
        update = self._createMongoUpdate(attrs)
        with self._mongoOperationHandling('Failed to update board'):
            result = self._db['boards'].update_many(fil, update)

        return dict(
            matchedCount=result.matched_count,
            updatedCount=result.modified_count,
        )

    def deleteBoard(self, searchFilter):
        query = searchFilter.getMongoFilter()

        with self._mongoOperationHandling('Failed to create post'):
            result = self._db['boards'].delete_many(query)

        return dict(deleteCount=result.deleted_count)

    def _createMongoUpdate(self, updateProps):
        update = defaultdict(lambda: defaultdict(int))
        fieldUpdates = updateProps.copy()
        incrementField = fieldUpdates.pop('increment', None)

        for field, value in fieldUpdates.items():
            update['$set'][field] = value
        if incrementField is not None:
            update['$inc'][incrementField] = 1
        
        return update

    def _createCounterQuery(self, fieldname):
        return dict(
            fieldname={ '$eq': fieldname }
        )

    def _getCounterAndIncrement(self, fieldname):
        counterQuery = self._createCounterQuery(fieldname)
        update = { '$inc': { 'value': 1 } }
        counterValue = self._db['counters'].find_one_and_update(counterQuery, update)

        return counterValue['value']

    @contextmanager
    def _mongoOperationHandling(self, errormsg):
        try:
            yield
        except Exception as e:
            logger.error(e)
            raise exceptions.FailedMongoOperation(errormsg)

    def _setDefaultSearchOptions(self, options):
        if 'paging' not in options:
            options['paging'] = Paging()
        if 'sorter' not in options:
            options['sorter'] = NullSorter()

    def _convertInnerIdToStr(self, entities):
        for entity in entities:
            entity['_id'] = str(entity['_id'])
