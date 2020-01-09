import json
import urllib.parse
import pytest
from flask import request

from server import server
import tests.mocks as mocks
import server.app_utils as app_utils
import server.exceptions as exceptions

@pytest.fixture(scope='function')
def app():
    app = server.setupApp()
    
    # make sure exceptions propagate to the test client
    app.testing = True

    # replace with mock
    app.config['DATABASE_OBJECT'] = mocks.createMockDB()
    app.config['SEARCH_FILTER'] = mocks.createMockFilter()
    app.config['PAGING'] = mocks.createMockPaging()

    yield app

class TestServerAPIs:
    def test_helloWorld(self, app):
        rv = app.test_client().get('/')
        assert 'hello world!' == rv.data.decode('utf-8')

    def test_jsonAPI(self, app):
        rv = app.test_client().get('/jsonstring')
        # json = r'{ "name": "Danny", "age": "13", "families": ["mother", "father", "sister"]}'
        data = json.loads( rv.data.decode('utf-8') )

        assert data['name'] == 'Danny'
        assert data['age'] == '13'
        assert len(data['families']) == 3
        assert data['families'][1] == 'father'

    def test_postJson(self, app):
        jsonData = {
            'name': 'postJson',
            'age': '1'
        }
        serialized = json.dumps(jsonData).encode('ascii')
        headers = {'content-type': 'application/json'}
        
        with app.test_client() as client:
            # client.post('/post', json=jsonData) # simple solution when posting json data
            client.post('/post', headers=headers, data=serialized) # a more general approach where specifying mime-type and payload
        
            data = request.get_json()
            assert data['name'] == jsonData['name']
            assert data['age'] == jsonData['age']

    def test_post_ifDBThrowsErrorReturn500(self, app):
        jsonData = {
            'author': 'someone',
            'message': 'Hello world'
        }
        db = app_utils.getDB(app)
        db.createPost.side_effect = Exception('Went wrong')

        with app.test_client() as client:
            rv = client.post('/api/post', json=jsonData)

            assert rv.status_code == 500

    def test_post_form(self, app):
        formData = urllib.parse.urlencode({
            'author': 'someone',
            'message': 'Hello world'
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }

        with app.test_client() as client:
            client.post('/post', data=formData, headers=header)

            assert request.form['author'] == 'someone'
            assert request.form['message'] == 'Hello world'

    def test_post_form_withoutHeadersReturn500(self, app):
        formData = urllib.parse.urlencode({
            'userId': '112233',
            'content': 'This is a post by 112233 for test'
        })

        with app.test_client() as client:
            response = client.post('/api/post', data=formData)

            assert request.form == {}
            assert response.status_code == 500

    def test_postCallsCreatePostOnDB(self, app):
        formData = urllib.parse.urlencode({
            'userId': '112233',
            'content': 'This is a post by 112233 for test'
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }

        with app.test_client() as client:
            response = client.post('/api/post', data=formData, headers=header)
            assert response.status_code == 200
            
            mockDB = app_utils.getDB(app)
            assert mockDB.createPost.call_count == 1

            passedPost = mockDB.createPost.call_args[0][0]
            assert passedPost['userId'] == '112233'
            assert passedPost['content'] == 'This is a post by 112233 for test'
            assert 'postId' in passedPost.keys()

    def test_postAPICallsDeletePostOnDBWhenDELETE(self, app):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }
        
        with app.test_client() as client:
            response = client.delete('/api/post', data=formData, headers=header)
            assert response.status_code == 200

            mockDB = app_utils.getDB(app)
            assert mockDB.deletePost.call_count == 1

    def test_postAPICallsSearchPostOnDBWhenGET(self, app):
        searchCriteria = {
            'postId': '0',
        }

        with app.test_client() as client:
            response = client.get('/api/post', query_string=searchCriteria)
            assert response.status_code == 200

            mockDB = app_utils.getDB(app)
            assert mockDB.searchPost.call_count == 1

    def test_postAPICallsUpdatePostOnDBWhenPATCH(self, app):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }
        
        with app.test_client() as client:
            response = client.patch('/api/post', data=formData, headers=header)
            assert response.status_code == 200
            
            # mockDB = app_utils.getDB(app)
            # assert mockDB.updatePost.call_count == 1

class TestPostsAPI:
    POSTSAPI_BASE_URL = '/v1/posts'

    def test_searchPostsAPI(self, app):
        mockDB = app_utils.getDB(app)
        mockDB.searchPost.return_value = ['post1', 'post2']
        mockFilter = app_utils.getFilter(app)
        mockFilter.createFilter.return_value = 'mockfilter'
        mockPaging = app_utils.getPaging(app)
        mockPaging.return_value = 'mockPaging'

        with app.test_client() as client:
            search = {
                'search': '1 2 3 4'
            }
            response = client.get(self.POSTSAPI_BASE_URL, query_string=search)

            # check response
            assert response.status_code == 200

            # check arguments passed to searchPost
            assert mockDB.searchPost.call_count == 1
            firstArg = mockDB.searchPost.call_args[0][0]
            assert firstArg == [mockFilter.createFilter.return_value]
            secondArg = mockDB.searchPost.call_args[0][1]
            assert secondArg == mockPaging.return_value

            # check correct filter was created
            assert mockFilter.createFilter.call_args[0][0]['value'] == ['1', '2', '3', '4']

            # check posts returned
            responseBodyJSON = response.get_json()
            assert responseBodyJSON['posts'] == mockDB.searchPost.return_value

    def test_searchPostsWithoutSearchStringReturnsNothing(self, app):
        with app.test_client() as client:
            response = client.get(self.POSTSAPI_BASE_URL)

            assert response.status_code == 400

            responseBodyJSON = response.get_json()
            assert responseBodyJSON['posts'] == []

    def test_searchPostsWithEmptySearchReturnsNothing(self, app):
        with app.test_client() as client:
            search = {
                'search': ''
            }
            response = client.get(self.POSTSAPI_BASE_URL, query_string=search)

            assert response.status_code == 400

            responseBodyJSON = response.get_json()
            assert responseBodyJSON['posts'] == []

    def test_whenSearchPostsRaisesErrorReturnsError(self, app):
        mockDB = app_utils.getDB(app)
        search = {
            'search': '1 2 3 4'
        }
        exceptionsToTest = [
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error')
        ]

        for e in exceptionsToTest:
            mockDB.searchPost.side_effect = e
            with app.test_client() as client:
                response = client.get(self.POSTSAPI_BASE_URL, query_string=search)

                assert response.status_code == e.getStatusCode()


    def test_searchPostsByExplicitIDReturns1Post(self, app):
        postId = 'aaabbb90'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        mockDB = app_utils.getDB(app)
        mockDB.searchPost.return_value = ['user1']
        mockFilter = app_utils.getFilter(app)
        mockFilter.createFilter.return_value = 'testFilter'

        with app.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200

            # make sure searchPost was called
            assert mockDB.searchPost.call_count == 1
            firstArg = mockDB.searchPost.call_args[0][0]
            assert firstArg == [mockFilter.createFilter.return_value]

            # make sure correct filter was created
            assert mockFilter.createFilter.call_count == 1
            firstArg = mockFilter.createFilter.call_args[0][0]
            assert firstArg['value'] == [postId]

            # returns post
            responseBodyJSON = response.get_json()
            assert responseBodyJSON['posts'] == mockDB.searchPost.return_value

    def test_searchPostsByExplicitIDReturnsErrorWhenExceptionRaised(self, app):
        mockDB = app_utils.getDB(app)
        postId = 'aaabbb90'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        
        exceptionsToTest = [
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]

        for e in exceptionsToTest:
            mockDB.searchPost.side_effect = e
            with app.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createPostReturnCreatedPost(self, app):
        url = f'{self.POSTSAPI_BASE_URL}/create'
        newPostData = {
            'userId': '0',
            'content': 'This is a test post',
        }
        headers = { 'content-type': 'application/x-www-form-urlencoded' }

        mockDB = app_utils.getDB(app)
        mockDB.createPost.return_value = 'post created'

        with app.test_client() as client:
            response = client.post(url, data=newPostData, headers=headers)

            assert response.status_code == 201

            assert mockDB.createPost.call_count == 1
            argPassed = mockDB.createPost.call_args[0][0]
            assert argPassed['userId'] == newPostData['userId']
            assert argPassed['content'] == newPostData['content']

            # returns post
            responseBodyJSON = response.get_json()
            assert responseBodyJSON['posts'] == [mockDB.createPost.return_value]

    def test_whenCreatePostRaisesExceptionReturnsError(self, app):
        mockDB = app_utils.getDB(app)
        url = f'{self.POSTSAPI_BASE_URL}/create'
        newPostData = {
            'userId': '0',
            'content': 'This is a test post',
        }
        headers = { 'content-type': 'application/x-www-form-urlencoded' }
        exceptionsToTest = [
            exceptions.EntityValidationError('Some error happened'),
            exceptions.ServerMiscError('Some error happened')
        ]

        for e in exceptionsToTest:
            mockDB.createPost.side_effect = e
            with app.test_client() as client:
                response = client.post(url, data=newPostData, headers=headers)

                assert response.status_code == e.getStatusCode()

    def test_updatePostReturnsStatus200(self, app):
        mockDB = app_utils.getDB(app)
        mockDB.updatePost.return_value = 'this is a post'

        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }

        with app.test_client() as client:
            response = client.patch(url, json=updateData)

            assert response.status_code == 200

            assert mockDB.updatePost.call_count == 1
            passedPostProperties = mockDB.updatePost.call_args[0][0]
            assert 'postId' in passedPostProperties
            assert 'content' in passedPostProperties
            assert passedPostProperties['postId'] == postIdToUpdate
            assert passedPostProperties['content'] == updateData['content']

    def test_updatePostByPostedMimeTypeNotJsonReturnsError(self, app):
        mockDB = app_utils.getDB(app)
        mockDB.updatePost.return_value = 'this is a post'

        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = 'content'
        headers={ 'content-type': 'text/plain'}

        with app.test_client() as client:
            response = client.patch(url, data=updateData, headers=headers)

            assert response.status_code == 400

    def test_whenUpdatePostRaisesExceptionReturnError(self, app):
        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }
        exceptionsToTest = [
            exceptions.EntityValidationError('Some error'),
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]

        for e in exceptionsToTest:
            app_utils.getDB(app).updatePost.side_effect = e
            with app.test_client() as client:
                response = client.patch(url, json=updateData)

                assert response.status_code == e.getStatusCode()

    def test_deletePostReturns200(self, app):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        mockDB = app_utils.getDB(app)

        with app.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200

            assert mockDB.deletePost.call_count == 1
            argPassed = mockDB.deletePost.call_args[0][0]
            assert argPassed == [postIdToDelete]

    def test_whenDeletePostRaisesExceptionReturnsError(self, app):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]
        mockDB = app_utils.getDB(app)

        for e in exceptionsToTest:
            mockDB.deletePost.side_effect = e
            with app.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()

class TestUserAPIs:
    USERAPI_BASE_URL = '/v1/users'

    def test_searchUsersReturnUsers(self, app):
        # setup mock behavior
        mockDB = app_utils.getDB(app)
        mockFilter = app_utils.getFilter(app)
        mockDB.searchUser.return_value = 'user found'
        mockFilter.createFilter.return_value = 'mock filter'

        query = {
            'search': 'myusername hisusername herusername'
        }

        with app.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=query)

            assert response.status_code == 200

            assert mockDB.searchUser.call_count == 1
            arg1Passed = mockDB.searchUser.call_args[0][0]
            assert len(arg1Passed)  == 1
            assert arg1Passed[0] == mockFilter.createFilter.return_value

            responseJson = response.get_json()
            assert responseJson['users'] == mockDB.searchUser.return_value

    def test_searchUsersReturnsErrorWhenFilterCreationRaisesException(self, app):
        # setup mock
        app_utils.getFilter(app).createFilter.side_effect = exceptions.FilterParseError('some error')
        
        query = {
            'search': 'myusername hisusername herusername'
        }

        with app.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=query)

            assert response.status_code ==  app_utils.getFilter(app).createFilter.side_effect.getStatusCode()

    def test_searchUsersReturnErrorWhenSearchRaisesException(self, app):
        # setup mock
        mockFilter = app_utils.getFilter(app)
        mockFilter.createFilter.return_value = 'mock filter'

        query = {
            'search': 'myusername hisusername herusername'
        }

        exceptionsToTest = [
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            app_utils.getDB(app).searchUser.side_effect = e
            with app.test_client() as client:
                response = client.get(self.USERAPI_BASE_URL, query_string=query)

                response.status_code == e.getStatusCode()

    def test_searchUserReturnsErrorWhenNoQuerystringProvided(self, app):
        # setup mock behavior
        mockDB = app_utils.getDB(app)
        mockFilter = app_utils.getFilter(app)
        mockDB.searchUser.return_value = 'user found'
        mockFilter.createFilter.return_value = 'mock filter'

        with app.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL)

            assert response.status_code == 400

    def test_searchUserByExplicitID(self, app):
        # setup mock
        mockDB = app_utils.getDB(app)
        mockDB.searchUser.return_value = 'user found'
        mockFilter = app_utils.getFilter(app)
        mockFilter.createFilter.return_value = 'mock filter'

        userId = '112233'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with app.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200

            assert mockDB.searchUser.call_count == 1
            arg1Passed = mockDB.searchUser.call_args[0][0]
            assert arg1Passed == [ mockFilter.createFilter.return_value ]

            jsonResponse = response.get_json()
            assert jsonResponse['users'] == mockDB.searchUser.return_value

    def test_searchUserByExplicitIDReturnsErrorWhenSearchUserRaisesException(self, app):
        userId = '112233'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        exceptionsToTest = [
            exceptions.EntityValidationError('some error'),
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            app_utils.getDB(app).searchUser.side_effect = e

            with app.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_searchUserExplciitIDReturnsErrorWhenSearchFilterRaisesException(self, app):
        # setup mock
        exceptionToTest = exceptions.FilterParseError('some error')
        mockFilter = app_utils.getFilter(app)
        mockFilter.createFilter.side_effect = exceptionToTest

        userId = '112233'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with app.test_client() as client:
            response = client.get(url)

            assert response.status_code == exceptionToTest.getStatusCode()

    def test_createUserReturns200(self, app):
        mockDB = app_utils.getDB(app)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'Joe',
            'password': '12345678'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = f'{self.USERAPI_BASE_URL}/create'

        with app.test_client() as client:
            response = client.post(url, data=userProperties, headers=headers)

            assert response.status_code == 200
            
            assert mockDB.createUser.call_count == 1
            arg1Passed = mockDB.createUser.call_args[0][0]
            for prop in userProperties.keys():
                assert arg1Passed[prop] == userProperties[prop]

    def test_createUserReturnsErrorWhenCreateUserThrowsException(self, app):
        mockDB = app_utils.getDB(app)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'Joe',
            'password': '12345678'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = f'{self.USERAPI_BASE_URL}/create'
        exceptionsToTest = [
            exceptions.EntityValidationError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            mockDB.createUser.side_effect = e
            with app.test_client() as client:
                response = client.post(url, data=userProperties, headers=headers)

                assert response.status_code == e.getStatusCode()

    def test_updateUserReturns200(self, app):
        mockDB = app_utils.getDB(app)
        userProperties = {
            'displayName': 'Jimmy',
        }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'

        with app.test_client() as client:
            response = client.patch(url, json=userProperties)

            assert response.status_code == 200

            assert mockDB.updateUser.call_count == 1
            arg1Passed = mockDB.updateUser.call_args[0][0]
            for prop in userProperties.keys():
                assert arg1Passed[prop] == userProperties[prop]
            assert arg1Passed['userId'] == userIdToUpdate

    def test_updateUserReturnsErrorWhenNonJsonPassed(self, app):
        requestDataToTest = [
            json.dumps({ 'displayName': 'Jimmy' }),
            'some_random_string'
        ]
        headersToTest = [
            { 'Content-Type': 'text/plain' },
            { 'Content-Type': 'application/json' },
        ]
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'

        for data, header in zip(requestDataToTest, headersToTest):
            with app.test_client() as client:
                response = client.patch(url, data=data, headers=header)

                assert response.status_code == 400

    def test_updateUserReturnsErrorWhenUpdateUserRaisesException(self, app):
        mockDB = app_utils.getDB(app)
        userProperties = {
            'displayName': 'Jimmy',
        }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'
        exceptionsToTest = [
            exceptions.EntityValidationError('some error'),
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            mockDB.updateUser.side_effect = e
            with app.test_client() as client:
                response = client.patch(url, json=userProperties)

                assert response.status_code == e.getStatusCode()

    def test_deleteUserReturns200(self, app):
        mockDB = app_utils.getDB(app)
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'

        with app.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200

            assert mockDB.deleteUser.call_count == 1
            arg1Passed = mockDB.deleteUser.call_args[0][0]
            assert arg1Passed == [userIdToDelete]

    def test_deleteUserReturnsErrorWhenDeleteUserRaisesException(self, app):
        mockDB = app_utils.getDB(app)
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            mockDB.deleteUser.side_effect = e
            with app.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()