import sys
import json
import urllib.parse
from pathlib import Path
import shutil
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[3]
TESTDATA = PROJECT_DIR / 'server' / 'database' / 'tests' / 'testdata.json'

sys.path.append( str(PROJECT_DIR / 'server') )
from database.simplefile import SimpleFile

@pytest.fixture(scope='function')
def setup():
    saveLocation = Path(__file__).resolve().parents[0] / 'temp'
    shutil.rmtree(saveLocation)
    saveLocation.mkdir(exist_ok=True)

    usersFile = saveLocation / SimpleFile.USERS_FILENAME
    postsFile = saveLocation / SimpleFile.POSTS_FILENAME
    users = setupSampleUsers(usersFile)
    posts = setupSamplePosts(postsFile)

    yield {
        'SAVE_LOCATION': saveLocation,
        'USERS_FILE': usersFile,
        'POSTS_FILE': postsFile,
        'SIMPLE_FILE': SimpleFile(saveLocation),
        'USERS': users,
        'POSTS': posts,
    }

def setupSampleUsers(fileName):
    with TESTDATA.open('r', encoding='utf-8') as f:
        data = json.load(f)

    fileName.touch()
    with fileName.open('w', encoding='utf-8') as f:
        json.dump(data['users'], f)

    return data['users']

def setupSamplePosts(fileName):
    with TESTDATA.open('r', encoding='utf-8') as f:
        data = json.load(f)

    fileName.touch()
    with fileName.open('w', encoding='utf-8') as f:
        json.dump(data['posts'], f)

    return data['posts']

def readJson(filepath):
    with filepath.open('r', encoding='utf-8') as f:
        return json.load(f)

class FixtureUtilities:
    @staticmethod
    def validateCreatedUsers(setup):
        usersFile = setup['USERS_FILE']
        assert usersFile.exists()

        users = FixtureUtilities.getAllUsers(setup)
        assert len(users) == len( FixtureUtilities.getOriginalUsers(setup) )
        # assert users[0]['userId'] == '1'
        # assert users[0]['displayName'] == 'Daniel'
        # assert users[1]['userName'] == 'eugene@myforumwebapp.com'

    @staticmethod
    def validateCreatedPosts(setup):
        postsFile = setup['POSTS_FILE']
        assert postsFile.exists()
        
        posts = FixtureUtilities.getAllPosts(setup)
        assert len(posts) == len( FixtureUtilities.getOriginalPosts(setup) )
        # assert posts[0]['userId'] == '1'
        # assert posts[3]['post'] == 'Eugene\'s post 2'

    @staticmethod
    def getAllUsers(setup):
        return readJson( setup['USERS_FILE'] )

    @staticmethod
    def getOriginalUsers(setup):
        return setup['USERS']

    @staticmethod
    def getAllPosts(setup):
        return readJson( setup['POSTS_FILE'] )

    @staticmethod
    def getOriginalPosts(setup):
        return setup['POSTS']

    @staticmethod
    def getDB(setup):
        return setup['SIMPLE_FILE']

class TestFixture:
    def test_fixtureCreatedTempDir(self, setup):
        assert setup['SAVE_LOCATION'].exists()

    def test_fixtureCreatedUsers(self, setup):
        FixtureUtilities.validateCreatedUsers(setup)
        
    def test_fixtureCreatedPosts(self, setup):
        FixtureUtilities.validateCreatedPosts(setup)

class TestUsersAPI:
    def test_createUserShouldCreateUserInDB(self, setup):
        db = FixtureUtilities.getDB(setup)

        userProps = {
            'displayName': 'Timmy',
            'userName': 'timmy@myforumwebapp.com'
        }

        db.createUser(userProps)

        users = FixtureUtilities.getAllUsers(setup)
        assert len(users) == len(FixtureUtilities.getOriginalUsers(setup)) + 1

        createdUser = [user for user in users 
            if user['displayName'] == userProps['displayName']
            and user['userName'] == userProps['userName']]
        assert len(createdUser) == 1

    def test_deleteUserShouldRemoveUserFromDB(self, setup):
        db = FixtureUtilities.getDB(setup)

        userIdToDelete = '1'
        db.deleteUser(userIdToDelete)

        users = FixtureUtilities.getAllUsers(setup)
        assert len(users) == len(FixtureUtilities.getOriginalUsers(setup)) - 1

        userInDB = [user for user in users 
            if user['userId'] == userIdToDelete]
        assert len(userInDB) == 0

    def test_deleteUserShouldDeleteAllPostsAssociated(self, setup):
        db = FixtureUtilities.getDB(setup)

        userIdToDelete = '1'
        db.deleteUser(userIdToDelete)

        posts = FixtureUtilities.getAllPosts(setup)
        assert len(posts) == len(FixtureUtilities.getOriginalPosts(setup)) - 5

        postsBelongingToDeletedUser = [post for post in posts
            if post['userId'] == userIdToDelete
        ]
        assert len(postsBelongingToDeletedUser) == 0

    def test_deleteUserWithNonExistantId(self, setup):
        db = FixtureUtilities.getDB(setup)

        userIdToDelete = 'non_existant'
        db.deleteUser(userIdToDelete)

        FixtureUtilities.validateCreatedUsers(setup)

    def test_createPostShouldCreatePostInDB(self, setup):
        db = FixtureUtilities.getDB(setup)

        postToCreate = {
            'userId': '1',
            'post': 'This is a new post!'
        }
        db.createPost(postToCreate)

        posts = FixtureUtilities.getAllPosts(setup)
        assert len(posts) == len(FixtureUtilities.getOriginalPosts(setup)) + 1

        createdPost = [post for post in posts
            if post['userId'] == postToCreate['userId']
            and post['post'] == postToCreate['post']
        ]
        assert len(createdPost) == 1

    def test_deletePostShouldRemovePostFromDB(self, setup):
        db = FixtureUtilities.getDB(setup)

        postIdToDelete = '1'
        db.deletePost(postIdToDelete)

        posts = FixtureUtilities.getAllPosts(setup)
        assert len(posts) == len(FixtureUtilities.getOriginalPosts(setup)) - 1
        
        postsShouldHaveBeenDeleted = [post for post in posts
            if post['postId'] == postIdToDelete
        ]
        assert len(postsShouldHaveBeenDeleted) == 0

    def test_deletePostWithNonExistantId(self, setup):
        db = FixtureUtilities.getDB(setup)

        postIdToDelete = 'non_existant'
        db.deletePost(postIdToDelete)

        FixtureUtilities.validateCreatedPosts(setup)