import json
import time

from server.database.database import Database
from server.database.filter import Filter
from server.database.paging import Paging, PagingNoLimit
from server.entity.user import NewUser
from server.entity.post import NewPost
from server.exceptions import EntityValidationError, ServerMiscError

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

class SimpleFile(Database):
    USERS_FILENAME = 'users.json'
    POSTS_FILENAME = 'posts.json'
    THREADS_FILENAME = 'threads.json'

    def __init__(self, filePath):
        self._saveLocation = filePath
        self._usersFile = self.createIfNotExist(self._saveLocation / self.USERS_FILENAME)
        self._postsFile = self.createIfNotExist(self._saveLocation / self.POSTS_FILENAME)
        self._threadsFile = self.createIfNotExist(self._saveLocation / self.THREADS_FILENAME)

    def createIfNotExist(self, filePath):
        if not filePath.exists():
            with filePath.open('w', encoding='utf-8') as f:
                json.dump([], f)

        return filePath

    def createUser(self, user):
        user['createdAt'] = time.time()
        if not NewUser.validate(user):
            raise EntityValidationError('failed to validate new user')
        
        self._createUserImpl(user)

    def searchUser(self, searchFilters, paging = Paging()):
        if len(searchFilters) == 0:
            return []

        with self._usersFile.open('r', encoding='utf-8') as f:
            users = json.load(f)

        matchedUsers = []
        for user in users[paging.offset:]:
            matchedConditions = [ search.matches(user) for search in searchFilters ]
            if all(matchedConditions):
                matchedUsers.append(user)

        return matchedUsers[:paging.limit]

    def deleteUser(self, userIds):
        self._deleteUserImpl(userIds)

    def createPost(self, post):
        post['createdAt'] = time.time()
        if not NewPost.validate(post):
            raise EntityValidationError('failed to validate new post')

        self._createPostImpl(post)

    def searchPost(self, searchFilters, paging = Paging()):
        if len(searchFilters) == 0:
            return []

        with self._postsFile.open('r', encoding='utf-8') as f:
            posts = json.load(f)

        matchedPosts = []
        for post in posts[paging.offset:]:
            matchConditions = [search.matches(post) for search in searchFilters]
            if all(matchConditions):
                matchedPosts.append(post)

        return matchedPosts[:paging.limit]

    def deletePost(self, postIds):
        self._deletePostImpl(postIds)

    def updatePost(self, post):
        self._updatePostImpl(post)

    @updateJSONFileContent('_usersFile')
    def _createUserImpl(self, user, currentUsers = None):
        return [*currentUsers, user]

    @updateJSONFileContent('_usersFile')
    def _deleteUserImpl(self, userIds, currentUsers = None):
        # delete related posts
        postsToDelete = self.searchPost(
            [Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIds })], 
            PagingNoLimit()
        )
        self.deletePost( [post['postId'] for post in postsToDelete] )
        
        updatedUsers = [
            user for user in currentUsers
            if user['userId'] not in userIds
        ]
        return updatedUsers

    @updateJSONFileContent('_postsFile')
    def _createPostImpl(self, post, currentPosts = None):
        return [*currentPosts, post]

    @updateJSONFileContent('_postsFile')
    def _deletePostImpl(self, postIds, currentPosts = None):
        return [ post for post in currentPosts if post['postId'] not in postIds ]

    @updateJSONFileContent('_postsFile')
    def _updatePostImpl(self, post, currentPosts = None):
        postIdx = [
            idx for idx, p in enumerate(currentPosts)
            if p['postId'] == post['postId']
        ][0]
        updatedPosts = [*currentPosts]
        updatedPosts[postIdx]['content'] = post['content']
        return updatedPosts