import json
import urllib.parse
from pathlib import Path
import shutil
import pytest
import pdb

from server.database.simplefile import SimpleFile
from server.database.datacreator import DataCreator
from server.database.filter import Filter
from server.database.paging import Paging

PROJECT_DIR = Path(__file__).resolve().parents[3]
TESTDATA = PROJECT_DIR / 'server' / 'database' / 'tests' / 'testdata.json'

@pytest.fixture(scope='function')
def setupDB():
    saveLocation = Path(__file__).resolve().parents[0] / 'temp'
    shutil.rmtree(saveLocation)
    saveLocation.mkdir(exist_ok=True)

    yield SetupDB_SimpleFile(saveLocation)

class SetupDB_SimpleFile:
    def __init__(self, saveLocation):
        self._saveLocation = saveLocation
        self._usersFile = saveLocation / SimpleFile.USERS_FILENAME
        self._postsFile = saveLocation / SimpleFile.POSTS_FILENAME
        self._originalUsers = self.setupSampleUsers(self._usersFile)
        self._originalPosts = self.setupSamplePosts(self._postsFile)
        self._db = SimpleFile(saveLocation)

    def setupSampleUsers(self, fileName):
        with TESTDATA.open('r', encoding='utf-8') as f:
            data = json.load(f)

        fileName.touch()
        with fileName.open('w', encoding='utf-8') as f:
            json.dump(data['users'], f)

        return data['users']

    def setupSamplePosts(self, fileName):
        with TESTDATA.open('r', encoding='utf-8') as f:
            data = json.load(f)

        fileName.touch()
        with fileName.open('w', encoding='utf-8') as f:
            json.dump(data['posts'], f)

        return data['posts']

    def validateCreatedUsers(self):
        createdUsers = self.getAllUsers()
        assert self._usersFile.exists()
        assert len(createdUsers) == len(self.getOriginalUsers())

    def validateCreatedPosts(self):
        assert self._postsFile.exists()
        assert len(self.getAllPosts()) == len(self.getOriginalPosts())

    def getAllUsers(self):
        return self.readJson( self._usersFile )

    def getOriginalUsers(self):
        return self._originalUsers

    def getAllPosts(self):
        return self.readJson( self._postsFile )

    def getOriginalPosts(self):
        return self._originalPosts

    def getDB(self):
        return self._db

    def readJson(self, filepath):
        with filepath.open('r', encoding='utf-8') as f:
            return json.load(f)

class TestFixture:
    def test_fixtureCreatedUsers(self, setupDB):
        setupDB.validateCreatedUsers()
        
    def test_fixtureCreatedPosts(self, setupDB):
        setupDB.validateCreatedPosts()

class TestUsersAPI:
    def test_createUserShouldCreateUserInDB(self, setupDB):
        db = setupDB.getDB()

        userProps = {
            'displayName': 'Timmy',
            'userName': 'timmy@myforumwebapp.com'
        }

        db.createUser(userProps)

        users = setupDB.getAllUsers()
        assert len(users) == len(setupDB.getOriginalUsers()) + 1

        createdUser = [
            user for user in users 
            if user['displayName'] == userProps['displayName']
            and user['userName'] == userProps['userName']
        ]
        assert len(createdUser) == 1

    def test_deleteUserShouldRemoveUserFromDB(self, setupDB):
        db = setupDB.getDB()

        userIdToDelete = '1'
        db.deleteUser([userIdToDelete])

        users = setupDB.getAllUsers()
        assert len(users) == len(setupDB.getOriginalUsers()) - 1

        usersShouldHaveBeenDeleted = [
            user for user in users 
            if user['userId'] == userIdToDelete
        ]
        assert len(usersShouldHaveBeenDeleted) == 0

    def test_deleteUserShouldRemoveMultipleUsersFromDB(self, setupDB):
        db = setupDB.getDB()

        userIdsToDelete = ['1', '2', '3']
        db.deleteUser(userIdsToDelete)

        users = setupDB.getAllUsers()
        assert len(users) == len(setupDB.getOriginalUsers()) - len(userIdsToDelete)

        usersShouldHaveBeenDeleted = [
            user for user in users 
            if user['userId'] in userIdsToDelete
        ]
        assert len(usersShouldHaveBeenDeleted) == 0

    def test_deleteUserShouldDeleteAllPostsAssociated(self, setupDB):
        db = setupDB.getDB()

        userIdToDelete = '1'
        db.deleteUser([userIdToDelete])

        posts = setupDB.getAllPosts()
        assert len(posts) == len(setupDB.getOriginalPosts()) - DataCreator.getPostCountPerUser()

        postsBelongingToDeletedUser = [
            post for post in posts
            if post['userId'] == userIdToDelete
        ]
        assert len(postsBelongingToDeletedUser) == 0

    def test_deleteUserWithNonExistantIdShouldDoNothing(self, setupDB):
        db = setupDB.getDB()

        userIdToDelete = 'non_existant'
        db.deleteUser([userIdToDelete])

        setupDB.validateCreatedUsers()

class TestPostsAPI:
    def test_createPostShouldCreatePostInDB(self, setupDB):
        db = setupDB.getDB()

        postToCreate = {
            'userId': '1',
            'post': 'This is a new post!'
        }
        db.createPost(postToCreate)

        posts = setupDB.getAllPosts()
        assert len(posts) == len(setupDB.getOriginalPosts()) + 1

        createdPost = [
            post for post in posts
            if post['userId'] == postToCreate['userId']
            and post['post'] == postToCreate['post']
        ]
        assert len(createdPost) == 1

    def test_deletePostShouldRemovePostFromDB(self, setupDB):
        db = setupDB.getDB()

        postIdToDelete = '1'
        db.deletePost([postIdToDelete])

        posts = setupDB.getAllPosts()
        assert len(posts) == len(setupDB.getOriginalPosts()) - 1
        
        postsShouldHaveBeenDeleted = [
            post for post in posts
            if post['postId'] == postIdToDelete
        ]
        assert len(postsShouldHaveBeenDeleted) == 0

    def test_deletePostShouldRemoveMultiplePostFromDB(self, setupDB):
        db = setupDB.getDB()

        postIdsToDelete = ['1', '2', '3']
        db.deletePost(postIdsToDelete)

        posts = setupDB.getAllPosts()
        assert len(posts) == len(setupDB.getOriginalPosts()) - len(postIdsToDelete)
        
        postsShouldHaveBeenDeleted = [
            post for post in posts
            if post['postId'] in postIdsToDelete
        ]
        assert len(postsShouldHaveBeenDeleted) == 0

    def test_deletePostWithNonExistantIdShouldDoNothing(self, setupDB):
        db = setupDB.getDB()
        postIdToDelete = 'non_existant'
        db.deletePost([postIdToDelete])

        setupDB.validateCreatedPosts()

    def test_searchPostByPostIdsShouldReturnPostFromDB(self, setupDB):
        db = setupDB.getDB()
        searchFilters = [
            Filter.createFilter({ 'field': 'postId', 'operator': 'eq', 'value': ['1'] }),
        ]
        posts = db.searchPost(searchFilters)

        assert len(posts) == 1
        assert posts[0]['postId'] in ['1']

    def test_searchPostByMultiplePostIdsShouldReturnPostFromDB(self, setupDB):
        db = setupDB.getDB()
        searchFilters = [
            Filter.createFilter({ 'field': 'postId', 'operator': 'eq', 'value': ['1', '2'] }),
        ]
        posts = db.searchPost(searchFilters)

        assert len(posts) == 2
        for post in posts:
            assert post['postId'] in ['1', '2']

    def test_searchPostByNonExitantPostIdShouldReturnNothing(self, setupDB):
        db = setupDB.getDB()
        searchFilters = [
            Filter.createFilter({ 'field': 'postId', 'operator': 'eq', 'value': ['non_existant'] }),
        ]
        posts = db.searchPost(searchFilters)

        assert len(posts) == 0

    def test_searchPostWithoutExplicitPagingShouldReturnDefaultAmount(self, setupDB):
        db = setupDB.getDB()
        searchFilters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': ['0', '1', '2'] }),
        ]
        posts = db.searchPost(searchFilters)

        assert len(posts) == Paging.DEFAULT_LIMIT

    def test_searchPostWithExplicitPagingShouldBeLimited(self, setupDB):
        db = setupDB.getDB()
        paging = Paging({ 'offset': DataCreator.POSTCOUNT_PER_USER * 2 + 1, 'limit': DataCreator.POSTCOUNT_PER_USER })
        searchFilters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': ['0', '1', '2'] }),
        ]
        posts = db.searchPost(searchFilters, paging)

        assert len(posts) == DataCreator.POSTCOUNT_PER_USER - 1

    def test_searchPostByMultipleFiltersIsSearchedByAND(self, setupDB):
        db = setupDB.getDB()
        displayNameOfFirstUser = setupDB.getOriginalUsers()[0]['displayName']
        paging = Paging({ 'limit': DataCreator.POSTCOUNT_PER_USER * 3 })
        searchFilters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': ['0', '1', '2'] }),
            Filter.createFilter({ 'field': 'post', 'operator': 'fuzzy', 'value': [displayNameOfFirstUser] }),
        ]
        posts = db.searchPost(searchFilters, paging)

        assert len(posts) == DataCreator.POSTCOUNT_PER_USER

    def test_searchPostWithEmptyFiltersShouldReturNothing(self, setupDB):
        db = setupDB.getDB()
        searchFilters = []
        posts = db.searchPost(searchFilters)

        assert len(posts) == 0

    def test_updatePostUpdatesPostOnDB(self, setupDB):
        db = setupDB.getDB()
        postToUpdate = {
            'postId': '1',
            'post': 'Post 1 was updated for testing!'
        }
        db.updatePost(postToUpdate)

        postInDB = [
            post for post in setupDB.getAllPosts() 
            if post['postId'] == postToUpdate['postId']
        ][0]
        assert postInDB['post'] == postToUpdate['post']
