# -*- coding: utf-8 -*-
"""
This file houses tests for file_crudmanager.py and mongo_crudmanager.py
"""

import pytest

from tests.database.setup_crudmanager import Setup_FileCrudManager, Setup_MongoCrudManager
from tests.database.datacreator import DataCreator
from server.database.filter import PrimitiveFilter
from server.database.aggregate_filter import AggregateFilter
from server.database.paging import Paging
from server.entity.user import UpdateUser
from server.entity.post import UpdatePost
from server.exceptions import EntityValidationError, RecordNotFoundError

@pytest.mark.slow
@pytest.mark.parametrize('createDB', [Setup_FileCrudManager, Setup_MongoCrudManager], indirect=True)
class TestFixture:
    def test_fixtureCreatedUsers(self, setupDB):
        setupDB.validateCreatedUsers()

    def test_fixtureCreatedPosts(self, setupDB):
        setupDB.validateCreatedPosts()

@pytest.mark.slow
@pytest.mark.parametrize('createDB', [Setup_FileCrudManager, Setup_MongoCrudManager], indirect=True)
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
    def createUpdateUserProps(self, **kwargs):
        return createNewProps(self.DEFAULT_UPDATE_USER, **kwargs)

    def test_createUserShouldCreateUserInDB(self, setupDB):
        mockuserauth = setupDB.getMockUserAuth()
        mockuserauth.hashPassword.return_value = 'hashed'
        userProps = self.createNewUserProps()

        assert len( setupDB.findUsers('userName', [ userProps['userName'] ]) ) == 0
        
        setupDB.getDB().createUser(userProps)

        assert setupDB.getUserCount() == len( setupDB.getOriginalUsers() ) + 1
        createdUsers = setupDB.findUsers('userName', [ userProps['userName'] ])
        assert len(createdUsers) == 1
        createdUser = createdUsers[0]
        for prop, value in userProps.items():
            if prop == 'password':
                assert createdUser[prop] == 'hashed'
            else:
                assert createdUser[prop] == value
        assert mockuserauth.hashPassword.call_count == 1

    def test_createUserShouldHaveUserIdAndIncrementedCounter(self, setupDB):
        mockuserauth = setupDB.getMockUserAuth()
        mockuserauth.hashPassword.return_value = 'hashed'
        userProps = self.createNewUserProps()
        nextUserId = setupDB.getCounter('userId')

        setupDB.getDB().createUser(userProps)

        createdUser = setupDB.findUsers('userName', [ userProps['userName'] ])[0]

        assert setupDB.getCounter('userId') == nextUserId + 1
        assert createdUser['userId'] == str(nextUserId)

    def test_createUserWithoutRequiredPropertiesShouldRaiseException(self, setupDB):
        userProps = [
            self.createNewUserProps(userName=None),
            self.createNewUserProps(displayName=None),
            self.createNewUserProps(password=None),
            self.createNewUserProps(userName=None, displayName=None, password=None),
            self.createNewUserProps(address='5th street')
        ]

        for userProp in userProps:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().createUser(userProp)

    def test_createUserByWrongPropertyTypeShouldRaiseException(self, setupDB):
        userProps = [
            self.createNewUserProps(userName=1),
            self.createNewUserProps(userName='something'), # non-email string
            self.createNewUserProps(displayName=1),
            self.createNewUserProps(password=1),
        ]

        for userProp in userProps:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().createUser(userProp)

    def test_deleteUserShouldRemoveUserFromDB(self, setupDB):
        userIdToDelete = setupDB.getOriginalUsers()[0]['userId']

        assert len( setupDB.findUsers('userId', [userIdToDelete]) ) == 1
        
        setupDB.getDB().deleteUser([userIdToDelete])

        assert setupDB.getUserCount() == len(setupDB.getOriginalUsers()) - 1
        assert len( setupDB.findUsers('userId', [userIdToDelete]) ) == 0

    def test_deleteUserShouldRemoveMultipleUsersFromDB(self, setupDB):
        userIdsToDelete = [
            user['userId'] for user in setupDB.getOriginalUsers()[:3]
        ]

        assert len( setupDB.findUsers('userId', userIdsToDelete) ) == 3

        setupDB.getDB().deleteUser(userIdsToDelete)

        assert len( setupDB.findUsers('userId', userIdsToDelete) ) == 0

    def test_deleteUserWithNonExistantIdShouldDoNothing(self, setupDB):
        userIdToDelete = 'non_existant'

        setupDB.getDB().deleteUser([userIdToDelete])

        setupDB.validateCreatedUsers()

    def test_searchUserByUserIdShouldReturnUserFromDB(self, setupDB):
        userIdsToSearch = [ setupDB.getOriginalUsers()[0]['userId'] ]
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)

        result = setupDB.getDB().searchUser(searchFilter)
        users = result['users']

        assert len(users) == 1
        assert users[0]['userId'] == userIdsToSearch[0]
        assert result['matchedCount'] == 1
        assert result['returnCount'] == 1

    def test_searchUserByNonExistantUserIdShouldReturnZeroUsersFromDB(self, setupDB):
        userIdsToSearch = ['non_existant']
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)

        result = setupDB.getDB().searchUser(searchFilter)
        users = result['users']

        assert len(users) == 0
        assert result['matchedCount'] == 0
        assert result['returnCount'] == 0

    def test_searchUserBy2UserIdsShouldReturn2UsersFromDB(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:2]
        ]
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)

        result = setupDB.getDB().searchUser(searchFilter)
        users = result['users']

        assert len(users) == 2
        for user in users:
            assert user['userId'] in userIdsToSearch
        assert result['matchedCount'] == 2
        assert result['returnCount'] == 2

    def test_searchUserByNoFilterShouldReturnAllUsers(self, setupDB):
        searchFilter = None
        
        result = setupDB.getDB().searchUser(searchFilter)
        users = result['users']

        assert len(users) == len( setupDB.getOriginalUsers() )
        assert result['matchedCount'] == len( setupDB.getOriginalUsers() )
        assert result['returnCount'] == len( setupDB.getOriginalUsers() )

    def test_searchUserByContradictingAggregateFilterShouldReturnNoUsers(self, setupDB):
        searchFilter = AggregateFilter.createFilter('and', [
            createSearchFilter('userId', 'eq', ['1']),
            createSearchFilter('userId', 'eq', ['2']),
        ])

        result = setupDB.getDB().searchUser(searchFilter)
        users = result['users']

        assert len(users) == 0
        assert result['matchedCount'] == 0
        assert result['returnCount'] == 0

    def test_searchUserByAggregateOrFiltersShouldReturn2Users(self, setupDB):
        searchFilter = AggregateFilter.createFilter('or', [
            createSearchFilter('userId', 'eq', ['1']),
            createSearchFilter('userId', 'eq', ['2']),
        ])

        result = setupDB.getDB().searchUser(searchFilter)
        users = result['users']

        assert len(users) == 2
        assert result['matchedCount'] == 2
        assert result['returnCount'] == 2

    def test_searchUserBy10UserIdWith5LimitShouldReturn5Users(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:10]
        ]
        paging = Paging({ 'limit': 5 })
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)

        result = setupDB.getDB().searchUser(searchFilter, paging)

        users = result['users']
        assert len(users) == 5
        assert result['matchedCount'] == 10
        assert result['returnCount'] == 5

    def test_searchUserBy10UserIdWith5Limit8OffsetShouldReturn2Users(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:10]
        ]
        paging = Paging({ 'limit': 5, 'offset': 8 })
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)

        result = setupDB.getDB().searchUser(searchFilter, paging)

        users = result['users']
        assert len(users) == 2
        assert result['matchedCount'] == 10
        assert result['returnCount'] == 2

    def test_updateUserUpdatesUserOnDB(self, setupDB):
        mock = setupDB.getMockUserAuth()
        mock.hashPassword.return_value = 'hashed'
        userProps = self.createUpdateUserProps()

        setupDB.getDB().updateUser(userProps)

        updatedUser = setupDB.findUsers('userId', [ userProps['userId'] ])[0]
        for field, value in userProps.items():
            if field == 'password':
                assert updatedUser[field] == 'hashed'
            else:
                assert updatedUser[field] == value

    def test_updateUserByNonExistantIdRaisesException(self, setupDB):
        with pytest.raises(RecordNotFoundError):
            setupDB.getDB().updateUser( self.createUpdateUserProps(userId='non_existant') )

    def test_updateUserWithoutRequiredPropertiesRaisesException(self, setupDB):
        userUpdateProperties = [
            self.createUpdateUserProps(userId=None)
        ]

        for userUpdate in userUpdateProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updateUser(userUpdate)

    def test_updateUserByWrongUpdatePropertiesRaisesException(self, setupDB):
        userUpdateProperties = [
            self.createUpdateUserProps(userId=1),
            self.createUpdateUserProps(displayName=1),
            self.createUpdateUserProps(password=1),
        ]

        for userUpdate in userUpdateProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updateUser(userUpdate)

    def test_updateUserWithUnexpectedPropertiesRaisesException(self, setupDB):
        mock = setupDB.getMockUserAuth()
        mock.hashPassword.return_value = 'hashed'

        userUpdateProperties = [
            self.createUpdateUserProps(createdAt=30.11),
            self.createUpdateUserProps(userName='Smithy'),
            self.createUpdateUserProps(someExtraProperty='SomeExtra'),
        ]

        for userUpdate in userUpdateProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updateUser(userUpdate)

@pytest.mark.slow
@pytest.mark.parametrize('createDB', [Setup_FileCrudManager, Setup_MongoCrudManager], indirect=True)
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
        postProps = self.createNewPostProps()

        setupDB.getDB().createPost(postProps)

        assert setupDB.getPostCount() == len(setupDB.getOriginalPosts()) + 1
        createdPost = setupDB.findPosts('content', [ postProps['content'] ])
        assert len(createdPost) == 1
        for field, value in postProps.items():
            assert createdPost[0][field] == value

    def test_createPostShouldHavePostIdAndIncrementedCounter(self, setupDB):
        postProps = self.createNewPostProps()
        nextPostId = setupDB.getCounter('postId')

        setupDB.getDB().createPost(postProps)

        createdPost = setupDB.findPosts('content', [ postProps['content'] ])[0]

        assert setupDB.getCounter('postId') == nextPostId + 1
        assert createdPost['postId'] == str(nextPostId)

    def test_createPostWithoutRequiredPropertiesShouldRaiseException(self, setupDB):
        postsToCreate = [
            self.createNewPostProps(content=None),
            self.createNewPostProps(userId=None),
            self.createNewPostProps(content2='A test post'),
        ]

        for postToCreate in postsToCreate:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().createPost(postToCreate)

    def test_createPostWithWrongPropertyTypeShouldRaiseException(self, setupDB):
        postsToCreate = [
            self.createNewPostProps(userId=1),
            self.createNewPostProps(content=22),
        ]

        for postToCreate in postsToCreate:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().createPost(postToCreate)

    def test_deletePostShouldRemovePostFromDB(self, setupDB):
        postIdToDelete = setupDB.getOriginalPosts()[0]['postId']

        setupDB.getDB().deletePost([postIdToDelete])

        assert setupDB.getPostCount() == len(setupDB.getOriginalPosts()) - 1
        postsShouldHaveBeenDeleted = setupDB.findPosts('postId', [postIdToDelete])
        assert len(postsShouldHaveBeenDeleted) == 0

    def test_deletePostShouldRemoveMultiplePostFromDB(self, setupDB):
        postIdsToDelete = [
            post['postId'] for post in setupDB.getOriginalPosts()[:3]
        ]

        setupDB.getDB().deletePost(postIdsToDelete)

        assert setupDB.getPostCount() == len(setupDB.getOriginalPosts()) - len(postIdsToDelete)
        postsShouldHaveBeenDeleted = setupDB.findPosts('postId', postIdsToDelete)
        assert len(postsShouldHaveBeenDeleted) == 0

    def test_deletePostWithNonExistantIdShouldDoNothing(self, setupDB):
        postIdToDelete = 'non_existant'

        setupDB.getDB().deletePost([postIdToDelete])

        setupDB.validateCreatedPosts()

    def test_searchPostByPostIdsShouldReturnPostFromDB(self, setupDB):
        postIdsToSearch = [
            post['postId'] for post in setupDB.getOriginalPosts()[:1]
        ]
        searchFilter = createSearchFilter('postId', 'eq', postIdsToSearch)

        result = setupDB.getDB().searchPost(searchFilter)

        posts = result['posts']
        assert len(posts) == 1
        assert posts[0]['postId'] in postIdsToSearch
        assert result['returnCount'] == 1
        assert result['matchedCount'] == 1

    def test_searchPostByMultiplePostIdsShouldReturnPostFromDB(self, setupDB):
        postIdsToSearch = [
            post['postId'] for post in setupDB.getOriginalPosts()[:2]
        ]
        searchFilter = createSearchFilter('postId', 'eq', postIdsToSearch)

        result = setupDB.getDB().searchPost(searchFilter)

        posts = result['posts']
        assert len(posts) == 2
        for post in posts:
            assert post['postId'] in postIdsToSearch
        assert result['returnCount'] == 2
        assert result['matchedCount'] == 2

    def test_searchPostByNonExitantPostIdShouldReturnNoPosts(self, setupDB):
        searchFilter = createSearchFilter('postId', 'eq', ['non_existant'])

        result = setupDB.getDB().searchPost(searchFilter)

        posts = result['posts']
        assert len(posts) == 0
        assert result['returnCount'] == 0
        assert result['matchedCount'] == 0

    def test_searchPostWithoutExplicitPagingShouldReturnDefaultAmount(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:3]
        ]
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)

        result = setupDB.getDB().searchPost(searchFilter)

        posts = result['posts']
        assert len(posts) == Paging.DEFAULT_LIMIT
        assert result['returnCount'] == Paging.DEFAULT_LIMIT
        assert result['matchedCount'] == len(userIdsToSearch) * DataCreator.POSTCOUNT_PER_USER

    def test_searchPostWithExplicitPagingShouldBeLimited(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:3]
        ]
        searchFilter = createSearchFilter('userId', 'eq', userIdsToSearch)
        paging = Paging({ 'offset': DataCreator.POSTCOUNT_PER_USER * 2 + 1, 'limit': DataCreator.POSTCOUNT_PER_USER })

        result = setupDB.getDB().searchPost(searchFilter, paging)

        posts = result['posts']
        assert len(posts) == DataCreator.POSTCOUNT_PER_USER - 1
        assert result['returnCount'] == DataCreator.POSTCOUNT_PER_USER - 1
        assert result['matchedCount'] == len(userIdsToSearch) * DataCreator.POSTCOUNT_PER_USER

    def test_searchPostByAggregateAndFilter(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:3]
        ]
        displayNameOfFirstUser = setupDB.getOriginalUsers()[0]['displayName']
        searchFilter = AggregateFilter.createFilter('and', [
            createSearchFilter('userId', 'eq', userIdsToSearch),
            createSearchFilter('content', 'fuzzy', [displayNameOfFirstUser]),
        ])
        paging = Paging({ 'limit': DataCreator.POSTCOUNT_PER_USER * 3 })

        result = setupDB.getDB().searchPost(searchFilter, paging)

        posts = result['posts']
        assert len(posts) == DataCreator.POSTCOUNT_PER_USER
        assert result['returnCount'] == DataCreator.POSTCOUNT_PER_USER
        assert result['matchedCount'] == DataCreator.POSTCOUNT_PER_USER

    def test_searchPostByAggregateORFilter(self, setupDB):
        userIdsToSearch = [
            user['userId'] for user in setupDB.getOriginalUsers()[:3]
        ]
        displayNameOfFirstUser = setupDB.getOriginalUsers()[0]['displayName']
        searchFilter = AggregateFilter.createFilter('or', [
            createSearchFilter('userId', 'eq', userIdsToSearch),
            createSearchFilter('content', 'fuzzy', [displayNameOfFirstUser]),
        ])
        paging = Paging({ 'limit': DataCreator.POSTCOUNT_PER_USER * 3 })

        result = setupDB.getDB().searchPost(searchFilter, paging)

        posts = result['posts']
        assert len(posts) == DataCreator.POSTCOUNT_PER_USER * 3
        assert result['returnCount'] == DataCreator.POSTCOUNT_PER_USER * 3
        assert result['matchedCount'] == DataCreator.POSTCOUNT_PER_USER * 3

    def test_searchPostWithNoFilterShouldReturnDefaultCount(self, setupDB):
        searchFilter = None

        result = setupDB.getDB().searchPost(searchFilter)

        posts = result['posts']
        assert len(posts) == Paging.DEFAULT_LIMIT
        assert result['returnCount'] == Paging.DEFAULT_LIMIT
        assert result['matchedCount'] == len(setupDB.getOriginalPosts())

    def test_updatePostUpdatesPostOnDB(self, setupDB):
        postToUpdate = self.createUpdatePostProps()

        setupDB.getDB().updatePost(postToUpdate)

        postInDB = setupDB.findPosts('postId', [ postToUpdate['postId'] ])[0]
        for field in UpdatePost.getUpdatableFields():
            assert postInDB[field] == postToUpdate[field]

    def test_updatePostUpdatesWithNonUpdatablePropertyRaisesException(self, setupDB):
        updatePostProperties = [
            self.createUpdatePostProps(userId='112233'),
            self.createUpdatePostProps(createdAt=22.99),
            self.createUpdatePostProps(randomProp=2),
        ]

        for postProps in updatePostProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updatePost(postProps)

    def test_updatePostWithoutRequiredPropertiesRaisesException(self, setupDB):
        updatePostProperties = [
            self.createUpdatePostProps(postId=None),
        ]

        for postProps in updatePostProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updatePost(postProps)

    def test_updatePostByWrongPropertyTypeRaisesException(self, setupDB):
        updatePostProperties = [
            self.createUpdatePostProps(content=1),
            self.createUpdatePostProps(postId=2),
        ]

        for postProps in updatePostProperties:
            with pytest.raises(EntityValidationError):
                setupDB.getDB().updatePost(postProps)

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

def createSearchFilter(field, operator, values):
    return PrimitiveFilter.createFilter({
         'field': field,
         'operator': operator,
         'value': values
    })
