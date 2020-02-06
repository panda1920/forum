# -*- coding: utf-8 -*-
"""
This file houses class for file-based database system
Used during the early phases of development
"""


import json
import time

from server.database.crudmanager import CrudManager
from server.database.filter import Filter
from server.database.paging import Paging, PagingNoLimit
from server.entity.user import NewUser, UpdateUser
from server.entity.post import NewPost, UpdatePost
from server.exceptions import EntityValidationError, RecordNotFoundError

def updateJSONFileContent(filenameAttr):
    """
    The issue was that I was writing the code below over and over:
    1. read file content
    2. edit the content
    3. write the updated content back to the file
    1 and 3 is essentially the same every time.
    So the motivation was to isolate 2 from the rest of recurring code.
    This decorator helps achieve this.

    usage:
    @updateJSONFileContent(<filenameAttr>)
    def updateContent(self, arg, filecontent = None):
        ... # do something with filecontent and update it
        return updatedContent

    """
    def updateJSONFileContentDecorator(func):
        def wrapper(*args):
            filename = getattr(args[0], filenameAttr) # args[0] refers to self
            with filename.open('r', encoding='utf-8') as f:
                filecontent = json.load(f)

                updatedContent = func(*args, filecontent) # None wont appear in *args
            
            with filename.open('w') as f:
                json.dump(updatedContent, f)
        return wrapper
    return updateJSONFileContentDecorator

class FileCrudManager(CrudManager):
    USERS_FILENAME = 'users.json'
    POSTS_FILENAME = 'posts.json'
    THREADS_FILENAME = 'threads.json'

    def __init__(self, filePath, userauth):
        self._saveLocation = filePath
        self._usersFile = self.createIfNotExist(self._saveLocation / self.USERS_FILENAME)
        self._postsFile = self.createIfNotExist(self._saveLocation / self.POSTS_FILENAME)
        self._threadsFile = self.createIfNotExist(self._saveLocation / self.THREADS_FILENAME)
        self._userauth = userauth

    def createIfNotExist(self, filePath):
        if not filePath.exists():
            directoryPath = filePath.parents[0]
            directoryPath.mkdir(parents=True, exist_ok=True)
            with filePath.open('w', encoding='utf-8') as f:
                json.dump([], f)

        return filePath

    def createUser(self, user):
        user['createdAt'] = time.time()
        if not NewUser.validate(user):
            raise EntityValidationError('failed to validate new user object')
        
        self._createUserImpl(user)

    def searchUser(self, searchFilter, paging = Paging()):
        with self._usersFile.open('r', encoding='utf-8') as f:
            users = json.load(f)

        if searchFilter is None:
            matchedUsers = users
        else:
            matchedUsers = []
            for user in users:
                if searchFilter.matches(user):
                    matchedUsers.append(user)

        start = paging.offset
        end = None if paging.limit is None else start + paging.limit
        return {
            'users': matchedUsers[start:end],
            'returnCount': len(matchedUsers[start:end]),
            'matchedCount': len(matchedUsers),
        }

    def deleteUser(self, userIds):
        self._deleteUserImpl(userIds)

    def updateUser(self, user):
        if not UpdateUser.validate(user):
            raise EntityValidationError('Failed to validate user update object')
        
        self._updateUserImpl(user)

    def createPost(self, post):
        post['createdAt'] = time.time()
        if not NewPost.validate(post):
            raise EntityValidationError('failed to validate new post object')

        self._createPostImpl(post)

    def searchPost(self, searchFilter, paging = Paging()):
        with self._postsFile.open('r', encoding='utf-8') as f:
            posts = json.load(f)

        if searchFilter is None:
            matchedPosts = posts
        else:
            matchedPosts = []
            for post in posts:
                if searchFilter.matches(post):
                    matchedPosts.append(post)

        start = paging.offset
        end = None if paging.limit is None else start + paging.limit
        return {
            'posts': matchedPosts[start:end],
            'returnCount': len(matchedPosts[start:end]),
            'matchedCount': len(matchedPosts),
        }

    def deletePost(self, postIds):
        self._deletePostImpl(postIds)

    def updatePost(self, post):
        if not UpdatePost.validate(post):
            raise EntityValidationError('failed to validate post update object')

        self._updatePostImpl(post)

    @updateJSONFileContent('_usersFile')
    def _createUserImpl(self, user, currentUsers = None):
        user['password'] = self._userauth.hashPassword( user['password'] )
        return [*currentUsers, user]

    @updateJSONFileContent('_usersFile')
    def _deleteUserImpl(self, userIds, currentUsers = None):
        # delete related posts
        postsToDelete = self.searchPost(
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIds }), 
            PagingNoLimit()
        )['posts']
        self.deletePost( [post['postId'] for post in postsToDelete] )
        
        updatedUsers = [
            user for user in currentUsers
            if user['userId'] not in userIds
        ]
        return updatedUsers

    @updateJSONFileContent('_usersFile')
    def _updateUserImpl(self, user, currentUsers = None):
        updatedUsers = [*currentUsers]
        
        try:
            userIdxToUpdate = [
                idx for idx, u in enumerate(currentUsers)
                if u['userId'] == user['userId']
            ][0]
        except:
            raise RecordNotFoundError(f'User with id of {user["userId"]} was not found.')
        
        for field in UpdateUser.getUpdatableFields():
            if field == 'password':
                updatedUsers[userIdxToUpdate][field] = self._userauth.hashPassword( user[field] )
            else:
                updatedUsers[userIdxToUpdate][field] = user[field]
        
        return updatedUsers

    @updateJSONFileContent('_postsFile')
    def _createPostImpl(self, post, currentPosts = None):
        return [*currentPosts, post]

    @updateJSONFileContent('_postsFile')
    def _deletePostImpl(self, postIds, currentPosts = None):
        return [ post for post in currentPosts if post['postId'] not in postIds ]

    @updateJSONFileContent('_postsFile')
    def _updatePostImpl(self, post, currentPosts = None):
        updatedPosts = [*currentPosts]
        try:
            postIdxToUpdate = [
                idx for idx, p in enumerate(currentPosts)
                if p['postId'] == post['postId']
            ][0]
        except:
            raise RecordNotFoundError(f'Post by id of {post["postId"]} was not found')

        for field in UpdatePost.getUpdatableFields():
            updatedPosts[postIdxToUpdate][field] = post[field]
        
        return updatedPosts