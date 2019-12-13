import urllib.parse
import json
from pathlib import Path
import shutil
import pytest
import pdb

from server.database.simplefile import SimpleFile
from server.database.datacreator import DataCreator
from server.database.filter import Filter
from server.database.paging import Paging
from server.entity.user import UpdateUser
from server.entity.post import UpdatePost
from server.exceptions import EntityValidationError, RecordNotFoundError

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

class TestUserCRUD:
    DEFAULT_NEW_USER = {
        'displayName': 'Timmy',
        'userName': 'timmy@myforumwebapp.com',
        'password': '222',
    }
    DEFAULT_UPDATE_USER = {
        'userId': '1',
        'displayName': 'Timmy',
        'password': '222'
    }
    
    def createNewUserProps(self, **kwargs):
        return createNewProps(self.DEFAULT_NEW_USER, **kwargs)
    def createUpdateuserProps(self, **kwargs):
        return createNewProps(self.DEFAULT_UPDATE_USER, **kwargs)

    def test_createUserShouldCreateUserInDB(self, setupDB):
        db = setupDB.getDB()

        db.createUser(self.createNewUserProps())

        users = setupDB.getAllUsers()
        assert len(users) == len(setupDB.getOriginalUsers()) + 1

        createdUser = [
            user for user in users 
            if user['displayName'] == self.DEFAULT_NEW_USER['displayName']
            and user['userName'] == self.DEFAULT_NEW_USER['userName']
            and user['password'] == self.DEFAULT_NEW_USER['password']
        ]
        assert len(createdUser) == 1

    def test_createUserWithoutRequiredPropertiesShouldRaiseException(self, setupDB):
        db = setupDB.getDB()

        userProps = [
            self.createNewUserProps(userName=None),
            self.createNewUserProps(displayName=None),
            self.createNewUserProps(password=None),
            self.createNewUserProps(userName=None, displayName=None, password=None),
            self.createNewUserProps(address='5th street')
        ]

        for userProp in userProps:
            with pytest.raises(EntityValidationError):
                db.createUser(userProp)

    def test_createUserByWrongPropertyTypeShouldRaiseException(self, setupDB):
        db = setupDB.getDB()

        userProps = [
            self.createNewUserProps(userName=1),
            self.createNewUserProps(userName='something'), # non-email string
            self.createNewUserProps(displayName=1),
            self.createNewUserProps(password=1),
        ]

        for userProp in userProps:
            with pytest.raises(EntityValidationError):
                db.createUser(userProp)

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

    def test_searchUserByUserIdShouldReturnUserFromDB(self, setupDB):
        db = setupDB.getDB()

        userIdsToSearch = ['1']
        filters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIdsToSearch })
        ]
        users = db.searchUser(filters)

        assert len(users) == 1
        assert users[0]['userId'] == userIdsToSearch[0]

    def test_searchUserByNonExistantUserIdShouldReturnZeroUsersFromDB(self, setupDB):
        db = setupDB.getDB()

        userIdsToSearch = ['non_existant']
        filters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIdsToSearch })
        ]
        users = db.searchUser(filters)

        assert len(users) == 0

    def test_searchUserBy2UserIdsShouldReturn2UsersFromDB(self, setupDB):
        db = setupDB.getDB()

        userIdsToSearch = ['1', '2']
        filters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIdsToSearch })
        ]
        users = db.searchUser(filters)

        assert len(users) == 2
        for user in users:
            assert user['userId'] in userIdsToSearch

    def test_searchUserByNoFilterShouldReturnNoUsers(self, setupDB):
        db = setupDB.getDB()

        filters = []
        users = db.searchUser(filters)

        assert len(users) == 0

    def test_searchUserByContradictingFiltersShouldReturnNoUsers(self, setupDB):
        db = setupDB.getDB()

        filters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': ['1'] }),
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': ['2'] }),
        ]
        users = db.searchUser(filters)

        assert len(users) == 0

    def test_searchUserBy10UserIdWith5LimitShouldReturn5Users(self, setupDB):
        db = setupDB.getDB()

        userIdsToSearch = ['0', '1', '2', '3' ,'4', '5' ,'6' ,'7' ,'8' ,'9']
        paging = Paging({ 'limit': 5 })
        filters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIdsToSearch }),
        ]
        users = db.searchUser(filters, paging)

        assert len(users) == 5

    def test_searchUserBy10UserIdWith5Limit8OffsetShouldReturn2Users(self, setupDB):
        db = setupDB.getDB()

        userIdsToSearch = ['0', '1', '2', '3' ,'4', '5' ,'6' ,'7' ,'8' ,'9']
        paging = Paging({ 'limit': 5, 'offset': 8 })
        filters = [
            Filter.createFilter({ 'field': 'userId', 'operator': 'eq', 'value': userIdsToSearch }),
        ]
        users = db.searchUser(filters, paging)

        assert len(users) == 2

    def test_updateUserUpdateUserOnDB(self, setupDB):
        setupDB.getDB().updateUser( self.DEFAULT_UPDATE_USER )

        updatedUser = [
            user for user in setupDB.getAllUsers()
            if user['userId'] == self.DEFAULT_UPDATE_USER['userId']
        ][0]

        for field in UpdateUser.getUpdatableFields():
            assert updatedUser[field] == self.DEFAULT_UPDATE_USER[field]

    def test_updateUserByNonExistantIdRaisesError(self, setupDB):
        with pytest.raises(RecordNotFoundError):
            setupDB.getDB().updateUser( self.createUpdateuserProps(userId='non_existant') )

    def test_updateUserWithoutRequiredPropertiesThrowsAnError(self, setupDB):
        userUpdateProperties = [
            self.createUpdateuserProps(userId=None)
        ]

        for userUpdate in userUpdateProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updateUser(userUpdate)

    def test_updateUserByWrongUpdatePropertiesThrowsAnError(self, setupDB):
        userUpdateProperties = [
            self.createUpdateuserProps(userId=1),
            self.createUpdateuserProps(displayName=1),
            self.createUpdateuserProps(password=1),
        ]

        for userUpdate in userUpdateProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updateUser(userUpdate)

    def test_updateUserWithUnexpectedPropertiesHaveNoEffectOnUpdate(self, setupDB):
        updatableFields = UpdateUser.getUpdatableFields()

        userUpdatePropertiesAndUnExpectedPropertyName = [
            ( self.createUpdateuserProps(createdAt=30.11), 'createdAt' ),
            ( self.createUpdateuserProps(userName='Smithy'), 'userName' ),
            ( self.createUpdateuserProps(someExtraProperty='SomeExtra'), 'someExtraProperty' ),
        ]

        for update, propertyName in userUpdatePropertiesAndUnExpectedPropertyName:
            setupDB.getDB().updateUser(update)
            updatedUser = [
                user for user in setupDB.getAllUsers()
                if user['userId'] == update['userId']
            ][0]

            for field in updatableFields:
                assert updatedUser[field] == update[field]
            assert (
                propertyName not in updatedUser or
                updatedUser[propertyName] != update[propertyName]
            )

class TestPostCRUD:
    DEFAULT_NEW_POST = {
        'userId': '1',
        'content': 'This is a new post!'
    }
    DEFAULT_UPDATE_POST = {
        'postId': '1',
        'content': 'Post updated!'
    }
    
    def createNewPostProps(self, **kwargs):
        return createNewProps(self.DEFAULT_NEW_POST, **kwargs)
    
    def createUpdatePostProps(self, **kwargs):
        return createNewProps(self.DEFAULT_UPDATE_POST, **kwargs)

    def test_createPostShouldCreatePostInDB(self, setupDB):
        db = setupDB.getDB()
        postToCreate = self.createNewPostProps()
        db.createPost(postToCreate)

        posts = setupDB.getAllPosts()
        assert len(posts) == len(setupDB.getOriginalPosts()) + 1
        createdPost = [
            post for post in posts
            if post['userId'] == postToCreate['userId']
            and post['content'] == postToCreate['content']
        ]
        assert len(createdPost) == 1

    def test_createPostWithoutRequiredPropertiesShouldRaiseException(self, setupDB):
        db = setupDB.getDB()
        postsToCreate = [
            self.createNewPostProps(content=None),
            self.createNewPostProps(userId=None),
            self.createNewPostProps(content2='A test post'),
        ]

        for postToCreate in postsToCreate:
            with pytest.raises(EntityValidationError):
                db.createPost(postToCreate)

    def test_createPostWithWrongPropertyTypeShouldRaiseException(self, setupDB):
        db = setupDB.getDB()

        postsToCreate = [
            self.createNewPostProps(userId=1),
            self.createNewPostProps(content=22),
        ]

        for postToCreate in postsToCreate:
            with pytest.raises(EntityValidationError):
                db.createPost(postToCreate)

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
            Filter.createFilter({ 'field': 'content', 'operator': 'fuzzy', 'value': [displayNameOfFirstUser] }),
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
        postToUpdate = self.createUpdatePostProps()
        db.updatePost(postToUpdate)

        postInDB = [
            post for post in setupDB.getAllPosts() 
            if post['postId'] == postToUpdate['postId']
        ][0]

        for field in UpdatePost.getUpdatableFields():
            assert postInDB[field] == postToUpdate[field]

    def test_updatePostUpdatesWithExtraPropertiesPermittedButNotUsed(self, setupDB):
        db = setupDB.getDB()
        updatePostPropertiesAndExtraPropertyNames = [
            ( self.createUpdatePostProps(userId='112233'), 'userId' ),
            ( self.createUpdatePostProps(createdAt=22.99), 'createdAt' ),
            ( self.createUpdatePostProps(randomProp=2), 'randomProp' ),
        ]

        for postProps, extraPropName in updatePostPropertiesAndExtraPropertyNames:
            db.updatePost(postProps)
            postInDB = [
                post for post in setupDB.getAllPosts() 
                if post['postId'] == postProps['postId']
            ][0]

            for field in UpdatePost.getUpdatableFields():
                assert postInDB[field] == postProps[field]
            assert (
                extraPropName not in postInDB or
                postInDB[extraPropName] != postProps[extraPropName]
            )

    def test_updatePostWithoutRequiredPropertiesRaisesException(self, setupDB):
        db = setupDB.getDB()
        updatePostProperties = [
            self.createUpdatePostProps(postId=None),
        ]

        for postProps in updatePostProperties:
            with pytest.raises(EntityValidationError):
                db.updatePost(postProps)

    def test_updatePostByWrongPropertyTypeRaisesException(self, setupDB):
        db = setupDB.getDB()
        updatePostProperties = [
            self.createUpdatePostProps(content=1),
            self.createUpdatePostProps(postId=2),
        ]

        for postProps in updatePostProperties:
            with pytest.raises(EntityValidationError):
                db.updatePost(postProps)

    def test_updatePostByNonExistantIdRaisesException(self, setupDB):
        with pytest.raises(RecordNotFoundError):
            setupDB.getDB().updatePost( self.createUpdatePostProps(postId='non_existant') )


### utility functions here

def createNewProps(defaultProps, **kwargs):
    """
    helper to quickly create props for testing
    all kwargs are added to defaultProps,
    with exception to those with None, in which case the property is removed instead
    """
    props = defaultProps.copy()
    
    for prop in kwargs.keys():
        propertyValue = kwargs[prop]
        if propertyValue == None:
            props.pop(prop, None)
        else:
            props[prop] = propertyValue

    return props