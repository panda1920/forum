# -*- coding: utf-8 -*-
"""
This file houses class for file-based database system
Used during the early phases of development
"""
import json
import time
import logging

from server.database.sorter import NullSorter
from server.database.crudmanager import CrudManager
from server.database.paging import Paging
from server.entity.user import NewUser, UpdateUser
from server.entity.post import NewPost, UpdatePost
from server.entity.thread import NewThread, UpdateThread
from server.exceptions import EntityValidationError


def updateJSONFileContent(filenameAttr):
    """
    The issue was that I was writing the code below over and over:
    1. read file content
    2. edit the content
    3. write the updated content back to the file
    1 and 3 is essentially the same every time.
    So the motivation was to isolate step 2 from the rest of recurring code.
    This decorator helps achieve this.

    usage:
    @updateJSONFileContent(<filenameAttr>)
    def updateContent(self, arg, filecontent=None):
        ... # do something with filecontent and update it

    """
    def updateJSONFileContentDecorator(func):
        def wrapper(*args):
            filename = getattr(args[0], filenameAttr)  # args[0] refers to self
            with filename.open('r', encoding='utf-8') as f:
                filecontent = json.load(f)

            # update filecontent with func
            # None wont appear in *args
            response = func(*args, filecontent)
            
            with filename.open('w') as f:
                json.dump(filecontent, f)

            return response
        return wrapper
    return updateJSONFileContentDecorator


class FileCrudManager(CrudManager):
    USERS_FILENAME = 'users.json'
    POSTS_FILENAME = 'posts.json'
    THREADS_FILENAME = 'threads.json'
    COUNTERS_FILENAME = 'counters.json'

    def __init__(self, filePath, passwordService):
        self._saveLocation = filePath
        self._usersFile = self.createIfNotExist(self._saveLocation / self.USERS_FILENAME)
        self._postsFile = self.createIfNotExist(self._saveLocation / self.POSTS_FILENAME)
        self._threadsFile = self.createIfNotExist(self._saveLocation / self.THREADS_FILENAME)
        self._countersFile = self.createIfNotExist(self._saveLocation / self.COUNTERS_FILENAME)
        self._passwordService = passwordService

    def createIfNotExist(self, filePath):
        if not filePath.exists():
            directoryPath = filePath.parents[0]
            directoryPath.mkdir(parents=True, exist_ok=True)
            with filePath.open('w', encoding='utf-8') as f:
                json.dump([], f)

        return filePath

    def createUser(self, user):
        attrs = user.to_create()

        attrs['createdAt'] = time.time()
        attrs['password'] = self._passwordService.hashPassword( attrs['password'] )
        attrs['userId'] = str( self._getCounter('userId') )
        
        self._createUserImpl(attrs)
        self._incrementCounter('userId')

        return dict(
            createdCount=1,
            createdId=attrs['userId']
        )

    def searchUser(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')

        with self._usersFile.open('r', encoding='utf-8') as f:
            users = json.load(f)

        if searchFilter is None:
            matchedUsers = users
        else:
            matchedUsers = [
                user for user in users
                if searchFilter.matches(user)
            ]
        sortedUsers = sorter.sort(matchedUsers)
        returnUsers = paging.slice(sortedUsers)
        
        return {
            'users': returnUsers,
            'returnCount': len(returnUsers),
            'matchedCount': len(matchedUsers),
        }

    def deleteUser(self, searchFilter):
        return self._deleteUserImpl(searchFilter)

    def updateUser(self, searchFilter, user):
        if not UpdateUser.validate(user):
            logging.error(f'failed to validate error: {user}')
            raise EntityValidationError('Failed to validate user update object')
        
        return self._updateUserImpl(searchFilter, user)
        
    def createPost(self, post):
        if not NewPost.validate(post):
            logging.error(f'failed to validate error: {post}')
            raise EntityValidationError('failed to validate new post object')

        post['createdAt'] = time.time()
        post['postId'] = str( self._getCounter('postId') )

        self._createPostImpl(post)
        self._incrementCounter('postId')

        return dict(
            createdCount=1,
            createdId=post['postId'],
        )

    def searchPost(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')

        with self._postsFile.open('r', encoding='utf-8') as f:
            posts = json.load(f)

        if searchFilter is None:
            matchedPosts = posts
        else:
            matchedPosts = [
                post for post in posts
                if searchFilter.matches(post)
            ]
        sortedPosts = sorter.sort(matchedPosts)
        returnPosts = paging.slice(sortedPosts)

        return {
            'posts': returnPosts,
            'returnCount': len(returnPosts),
            'matchedCount': len(matchedPosts),
        }

    def deletePost(self, searchFilter):
        return self._deletePostImpl(searchFilter)

    def updatePost(self, searchFilter, post):
        if not UpdatePost.validate(post):
            logging.error(f'failed to validate error: {post}')
            raise EntityValidationError('failed to validate post update object')

        return self._updatePostImpl(searchFilter, post)

    def createThread(self, thread):
        if not NewThread.validate(thread):
            logging.error(f'failed to validate error: {thread}')
            raise EntityValidationError('failed to validate new thread object')
        
        thread['createdAt'] = time.time()
        thread['threadId'] = str( self._getCounter('threadId') )

        self._createThreadImpl(thread)
        self._incrementCounter('threadId')

        return dict(
            createdCount=1,
            createdId=thread['threadId'],
        )

    def searchThread(self, searchFilter, **options):
        self._setDefaultSearchOptions(options)
        paging = options.get('paging')
        sorter = options.get('sorter')

        with self._threadsFile.open('r', encoding='utf-8') as f:
            threads = json.load(f)

        if searchFilter is None:
            matchedThreads = threads
        else:
            matchedThreads = [
                thread for thread in threads
                if searchFilter.matches(thread)
            ]
        sortedThreads = sorter.sort(matchedThreads)
        returnThreads = paging.slice(sortedThreads)

        return dict(
            threads=returnThreads,
            matchedCount=len(matchedThreads),
            returnCount=len(returnThreads),
        )

    def updateThread(self, searchFilter, thread):
        if not UpdateThread.validate(thread):
            logging.error(f'failed to validate error: {thread}')
            raise EntityValidationError('Failed to validate thread update object')

        return self._updateThreadImpl(searchFilter, thread)

    def deleteThread(self, searchFilter):
        return self._deleteThreadImpl(searchFilter)

    @updateJSONFileContent('_usersFile')
    def _createUserImpl(self, user, currentUsers=None):
        currentUsers.append(user)

    @updateJSONFileContent('_usersFile')
    def _deleteUserImpl(self, searchFilter, currentUsers=None):
        deleteCount = 0

        def matches(user):
            isMatched = searchFilter.matches(user)
            if isMatched:
                nonlocal deleteCount
                deleteCount += 1
            return isMatched

        currentUsers[:] = [
            user for user in currentUsers
            if not matches(user)
        ]

        return dict(deleteCount=deleteCount)
                
    @updateJSONFileContent('_usersFile')
    def _updateUserImpl(self, searchFilter, user, currentUsers=None):
        # find out which element in list needs update
        userIdxToUpdate = [
            idx for idx, u in enumerate(currentUsers)
            if searchFilter.matches(u)
        ]
        
        # apply update
        for idx in userIdxToUpdate:
            for field in UpdateUser.getUpdatableFields():
                if field not in user:
                    continue
                if field == 'password':
                    hashed = self._passwordService.hashPassword( user[field] )
                    currentUsers[idx][field] = hashed
                else:
                    currentUsers[idx][field] = user[field]

        return dict(
            matchedCount=len(userIdxToUpdate),
            updatedCount=len(userIdxToUpdate),
        )
        
    @updateJSONFileContent('_postsFile')
    def _createPostImpl(self, post, currentPosts=None):
        currentPosts.append(post)

    @updateJSONFileContent('_postsFile')
    def _deletePostImpl(self, searchFilter, currentPosts=None):
        deleteCount = 0

        def matches(user):
            isMatched = searchFilter.matches(user)
            if isMatched:
                nonlocal deleteCount
                deleteCount += 1
            return isMatched

        currentPosts[:] = [
            post for post in currentPosts
            if not matches(post)
        ]

        return dict(deleteCount=deleteCount)

    @updateJSONFileContent('_postsFile')
    def _updatePostImpl(self, searchFilter, post, currentPosts=None):
        # determine which element in list needs update
        postIdxToUpdate = [
            idx for idx, p in enumerate(currentPosts)
            if searchFilter.matches(p)
        ]
        # apply update
        for idx in postIdxToUpdate:
            for field in UpdatePost.getUpdatableFields():
                currentPosts[idx][field] = post[field]

        return dict(
            matchedCount=len(postIdxToUpdate),
            updatedCount=len(postIdxToUpdate),
        )

    @updateJSONFileContent('_threadsFile')
    def _createThreadImpl(self, thread, currentThreads=None):
        currentThreads.append(thread)

    @updateJSONFileContent('_threadsFile')
    def _updateThreadImpl(self, searchFilter, update, currentThreads=None):
        threadIdxToUpdate = [
            idx for idx, t in enumerate(currentThreads)
            if searchFilter.matches(t)
        ]

        fieldUpdate = update.copy()
        incrementFieldToUpdate = update.pop('increment', None)

        for idx in threadIdxToUpdate:
            for field in fieldUpdate.keys():
                currentThreads[idx][field] = fieldUpdate[field]
            if incrementFieldToUpdate is not None:
                currentThreads[idx][incrementFieldToUpdate] += 1

        return dict(
            matchedCount=len(threadIdxToUpdate),
            updatedCount=len(threadIdxToUpdate),
        )

    @updateJSONFileContent('_threadsFile')
    def _deleteThreadImpl(self, searchFilter, currentThreads=None):
        deleteCount = 0

        def matches(thread):
            isMatched = searchFilter.matches(thread)
            if isMatched:
                nonlocal deleteCount
                deleteCount += 1
            return isMatched

        currentThreads[:] = [
            thread for thread in currentThreads
            if not matches(thread)
        ]

        return dict(deleteCount=deleteCount)

    def _getCounter(self, fieldname):
        with self._countersFile.open('r', encoding='utf-8') as f:
            counters = json.load(f)
            for counter in counters:
                if counter['fieldname'] == fieldname:
                    return counter['value']

    @updateJSONFileContent('_countersFile')
    def _incrementCounter(self, fieldname, currentCounters=None):
        for counter in currentCounters:
            if counter['fieldname'] == fieldname:
                counter['value'] += 1

    def _setDefaultSearchOptions(self, options):
        if 'paging' not in options:
            options['paging'] = Paging()
        if 'sorter' not in options:
            options['sorter'] = NullSorter()
