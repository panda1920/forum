import json
import urllib.parse
import pytest
from flask import request, current_app

from server import server
import tests.mocks as mocks
import server.app_utils as app_utils
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES = 'some_value'
DEFAULT_RETURN_CREATENEWPOST = None
DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES = 'some_value'
DEFAULT_RETURN_SIGNUP = None

@pytest.fixture(scope='function')
def mockApp(app):
    # replace with mock
    mockDB = mocks.createMockDB()
    app.config['DATABASE_OBJECT'] = mockDB

    mockCreate = mocks.createMockEntityCreationService()
    mockCreate.signup.return_value = DEFAULT_RETURN_SIGNUP
    mockCreate.createNewPost.return_value = DEFAULT_RETURN_CREATENEWPOST
    app.config['CREATION_SERVICE'] = mockCreate
    
    mockSearch = mocks.createMockSearchService()
    mockSearch.searchPostsByKeyValues.return_value = DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES
    mockSearch.searchUsersByKeyValues.return_value = DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES
    app.config['SEARCH_SERVICE'] = mockSearch

    yield app

@pytest.fixture(scope='function')
def client(mockApp):
    with mockApp.test_client() as client:
        yield client

class TestServerAPIs:
    def test_helloWorld(self, client):
        rv = client.get('/')
        assert 'hello world!' == rv.data.decode('utf-8')

    def test_jsonAPI(self, client):
        rv = client.get('/jsonstring')
        data = json.loads( rv.data.decode('utf-8') )

        assert data['name'] == 'Danny'
        assert data['age'] == '13'
        assert len(data['families']) == 3
        assert data['families'][1] == 'father'

    def test_postJson(self, client):
        jsonData = {
            'name': 'postJson',
            'age': '1'
        }
        serialized = json.dumps(jsonData).encode('ascii')
        headers = {'Content-Type': 'application/json'}
        
        # client.post('/post', json=jsonData) # simple solution when posting json data
        client.post('/post', headers=headers, data=serialized) # a more general approach where specifying mime-type and payload
    
        data = request.get_json()
        assert data['name'] == jsonData['name']
        assert data['age'] == jsonData['age']

    def test_post_ifDBThrowsErrorReturn500(self, mockApp, client):
        jsonData = {
            'author': 'someone',
            'message': 'Hello world'
        }
        db = app_utils.getDB(mockApp)
        db.createPost.side_effect = Exception('Went wrong')

        rv = client.post('/api/post', json=jsonData)

        assert rv.status_code == 500

    def test_post_form(self, client):
        formData = urllib.parse.urlencode({
            'author': 'someone',
            'message': 'Hello world'
        })
        header = { 'Content-Type': 'application/x-www-form-urlencoded' }

        client.post('/post', data=formData, headers=header)

        assert request.form['author'] == 'someone'
        assert request.form['message'] == 'Hello world'

    def test_post_form_withoutHeadersReturn500(self, client):
        formData = urllib.parse.urlencode({
            'userId': '112233',
            'content': 'This is a post by 112233 for test'
        })

        response = client.post('/api/post', data=formData)

        assert request.form == {}
        assert response.status_code == 500

    def test_postCallsCreatePostOnDB(self, mockApp, client):
        formData = urllib.parse.urlencode({
            'userId': '112233',
            'content': 'This is a post by 112233 for test'
        })
        header = { 'Content-Type': 'application/x-www-form-urlencoded' }

        response = client.post('/api/post', data=formData, headers=header)
        assert response.status_code == 200
        
        mockDB = app_utils.getDB(mockApp)
        assert mockDB.createPost.call_count == 1

        passedPost = mockDB.createPost.call_args[0][0]
        assert passedPost['userId'] == '112233'
        assert passedPost['content'] == 'This is a post by 112233 for test'
        assert 'postId' in passedPost.keys()

    def test_postAPICallsDeletePostOnDBWhenDELETE(self, mockApp, client):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'Content-Type': 'application/x-www-form-urlencoded' }
        
        response = client.delete('/api/post', data=formData, headers=header)
        assert response.status_code == 200

        mockDB = app_utils.getDB(mockApp)
        assert mockDB.deletePost.call_count == 1

    def test_postAPICallsSearchPostOnDBWhenGET(self, mockApp, client):
        searchCriteria = {
            'postId': '0',
        }

        response = client.get('/api/post', query_string=searchCriteria)
        assert response.status_code == 200

        mockDB = app_utils.getDB(mockApp)
        assert mockDB.searchPost.call_count == 1

    def test_postAPICallsUpdatePostOnDBWhenPATCH(self, mockApp, client):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'Content-Type': 'application/x-www-form-urlencoded' }
        
        response = client.patch('/api/post', data=formData, headers=header)
        assert response.status_code == 200
            
            # mockDB = app_utils.getDB(mockApp)
            # assert mockDB.updatePost.call_count == 1

    def test_userlistReturnsAllUsers(self, mockApp, client):
        users = [{'userName': '1'}, {'userName': '2'}]
        mockDB = app_utils.getDB(mockApp)
        mockDB.searchUser.return_value = users

        response = client.get('/userlist')
        assert response.status_code == 200
        jsonBody = response.get_json()
        assert jsonBody['users'] == users

class TestPostsAPI:
    POSTSAPI_BASE_URL = '/v1/posts'

    def test_searchPostsAPIPassesQueryStringToSearchService(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(keyValues)

    def test_searchPostsAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            assert response.status_code == 200
            jsonResponse = response.get_json()
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES

    def test_searchPostsReturnsErrorWhenExceptionWasRaised(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        keyValues = dict(
            search='1 2 3 4',
        )

        for e in exceptionsToTest:
            with mockApp.test_client() as client:
                mockSearch.searchPostsByKeyValues.side_effect = e()
                response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

                assert response.status_code == e.getStatusCode()

    def test_searchPostsAPIByIdPassesIdToSearchService(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def searchPostsByIdAPIIgnoresQueryString(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        keyValues = dict(offset=30, limit=100)

        with mockApp.test_client() as client:
            response = client.get(url, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def test_searchPostsByIdAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200
            jsonResponse = response.get_json()
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES

    def test_searchPostsByIdAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = app_utils.getSearchService(mockApp)
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        for e in exceptionsToTest:
            with mockApp.test_client() as client:
                mockSearch.searchPostsByKeyValues.side_effect = e()
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createPostAPIPassesPostedDataToService(self, mockApp):
        mockCreate = app_utils.getCreationService(mockApp)
        newPostData = dict(
            userId='0',
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

        with mockApp.test_client() as client:
            response = client.post(url, data=newPostData, headers=headers)

            mockCreate.createNewPost.assert_called_with(newPostData)

    def test_createPostAPIReturns201(self, mockApp):
        mockCreate = app_utils.getCreationService(mockApp)
        newPostData = dict(
            userId='0',
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

        with mockApp.test_client() as client:
            response = client.post(url, data=newPostData, headers=headers)

            assert response.status_code == 201

    def test_createPostAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockCreate = app_utils.getCreationService(mockApp)
        newPostData = dict(
            userId='0',
            content='This is a test post'
        )
        url = f'{self.POSTSAPI_BASE_URL}/create'
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        exceptionsToTest = [
            exceptions.EntityValidationError,
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError
        ]

        for e in exceptionsToTest:
            mockCreate.createNewPost.side_effect = e()
            with mockApp.test_client() as client:
                response = client.post(url, data=newPostData, headers=headers)

                assert response.status_code == e.getStatusCode()

    def test_updatePostReturnsStatus200(self, mockApp):
        mockDB = app_utils.getDB(mockApp)
        mockDB.updatePost.return_value = 'this is a post'

        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = {
            'content': 'Updated content!'
        }

        with mockApp.test_client() as client:
            response = client.patch(url, json=updateData)

            assert response.status_code == 200

            assert mockDB.updatePost.call_count == 1
            passedPostProperties = mockDB.updatePost.call_args[0][0]
            assert 'postId' in passedPostProperties
            assert 'content' in passedPostProperties
            assert passedPostProperties['postId'] == postIdToUpdate
            assert passedPostProperties['content'] == updateData['content']

    def test_updatePostByPostedMimeTypeNotJsonReturnsError(self, mockApp):
        mockDB = app_utils.getDB(mockApp)
        mockDB.updatePost.return_value = 'this is a post'

        postIdToUpdate = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToUpdate}/update'
        updateData = 'content'
        headers={ 'Content-Type': 'text/plain'}

        with mockApp.test_client() as client:
            response = client.patch(url, data=updateData, headers=headers)

            assert response.status_code == 400

    def test_whenUpdatePostRaisesExceptionReturnError(self, mockApp):
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
            app_utils.getDB(mockApp).updatePost.side_effect = e
            with mockApp.test_client() as client:
                response = client.patch(url, json=updateData)

                assert response.status_code == e.getStatusCode()

    def test_deletePostReturns200(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        mockDB = app_utils.getDB(mockApp)

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200

            assert mockDB.deletePost.call_count == 1
            argPassed = mockDB.deletePost.call_args[0][0]
            assert argPassed == [postIdToDelete]

    def test_whenDeletePostRaisesExceptionReturnsError(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('Some error'),
            exceptions.ServerMiscError('Some error'),
        ]
        mockDB = app_utils.getDB(mockApp)

        for e in exceptionsToTest:
            mockDB.deletePost.side_effect = e
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()

class TestUserAPIs:
    USERAPI_BASE_URL = '/v1/users'

    def test_searchUsersReturnUsers(self, mockApp):
        # setup mock behavior
        mockDB = app_utils.getDB(mockApp)
        mockFilter = app_utils.getFilter(mockApp)
        mockDB.searchUser.return_value = 'user found'
        mockFilter.createFilter.return_value = 'mock filter'

        query = {
            'search': 'myusername hisusername herusername'
        }

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=query)

            assert response.status_code == 200

            assert mockDB.searchUser.call_count == 1
            arg1Passed = mockDB.searchUser.call_args[0][0]
            assert len(arg1Passed)  == 1
            assert arg1Passed[0] == mockFilter.createFilter.return_value

            responseJson = response.get_json()
            assert responseJson['users'] == mockDB.searchUser.return_value

    def test_searchUsersReturnsErrorWhenFilterCreationRaisesException(self, mockApp):
        # setup mock
        app_utils.getFilter(mockApp).createFilter.side_effect = exceptions.FilterParseError('some error')
        
        query = {
            'search': 'myusername hisusername herusername'
        }

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=query)

            assert response.status_code ==  app_utils.getFilter(mockApp).createFilter.side_effect.getStatusCode()

    def test_searchUsersReturnErrorWhenSearchRaisesException(self, mockApp):
        # setup mock
        mockFilter = app_utils.getFilter(mockApp)
        mockFilter.createFilter.return_value = 'mock filter'

        query = {
            'search': 'myusername hisusername herusername'
        }

        exceptionsToTest = [
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            app_utils.getDB(mockApp).searchUser.side_effect = e
            with mockApp.test_client() as client:
                response = client.get(self.USERAPI_BASE_URL, query_string=query)

                response.status_code == e.getStatusCode()

    def test_searchUserReturnsErrorWhenNoQuerystringProvided(self, mockApp):
        # setup mock behavior
        mockDB = app_utils.getDB(mockApp)
        mockFilter = app_utils.getFilter(mockApp)
        mockDB.searchUser.return_value = 'user found'
        mockFilter.createFilter.return_value = 'mock filter'

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL)

            assert response.status_code == 400

    def test_searchUserByExplicitID(self, mockApp):
        # setup mock
        mockDB = app_utils.getDB(mockApp)
        mockDB.searchUser.return_value = 'user found'
        mockFilter = app_utils.getFilter(mockApp)
        mockFilter.createFilter.return_value = 'mock filter'

        userId = '112233'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200

            assert mockDB.searchUser.call_count == 1
            arg1Passed = mockDB.searchUser.call_args[0][0]
            assert arg1Passed == [ mockFilter.createFilter.return_value ]

            jsonResponse = response.get_json()
            assert jsonResponse['users'] == mockDB.searchUser.return_value

    def test_searchUserByExplicitIDReturnsErrorWhenSearchUserRaisesException(self, mockApp):
        userId = '112233'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        exceptionsToTest = [
            exceptions.EntityValidationError('some error'),
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            app_utils.getDB(mockApp).searchUser.side_effect = e

            with mockApp.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_searchUserExplciitIDReturnsErrorWhenSearchFilterRaisesException(self, mockApp):
        # setup mock
        exceptionToTest = exceptions.FilterParseError('some error')
        mockFilter = app_utils.getFilter(mockApp)
        mockFilter.createFilter.side_effect = exceptionToTest

        userId = '112233'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == exceptionToTest.getStatusCode()

    def test_createUserReturns200(self, mockApp):
        mockSignup = app_utils.getSignup(mockApp)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
            'password': '12345678'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = f'{self.USERAPI_BASE_URL}/create'

        with mockApp.test_client() as client:
            response = client.post(url, data=userProperties, headers=headers)

            assert response.status_code == 200
            assert mockSignup.signup.call_count == 1
            argPassed = mockSignup.signup.call_args[0][0]
            for field, value in argPassed.items():
                assert value == userProperties[field]
            

    def test_createUserReturnsErrorWhenSignupThrowsException(self, mockApp):
        mockSignup = app_utils.getSignup(mockApp)
        userProperties = {
            'userName': 'joe@myforumwebapp.com',
            'displayName': 'joe',
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
            mockSignup.signup.side_effect = e
            with mockApp.test_client() as client:
                response = client.post(url, data=userProperties, headers=headers)

                assert response.status_code == e.getStatusCode()

    def test_updateUserReturns200(self, mockApp):
        mockDB = app_utils.getDB(mockApp)
        userProperties = {
            'displayName': 'Jimmy',
        }
        userIdToUpdate = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToUpdate}/update'

        with mockApp.test_client() as client:
            response = client.patch(url, json=userProperties)

            assert response.status_code == 200

            assert mockDB.updateUser.call_count == 1
            arg1Passed = mockDB.updateUser.call_args[0][0]
            for prop in userProperties.keys():
                assert arg1Passed[prop] == userProperties[prop]
            assert arg1Passed['userId'] == userIdToUpdate

    def test_updateUserReturnsErrorWhenNonJsonPassed(self, mockApp):
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
            with mockApp.test_client() as client:
                response = client.patch(url, data=data, headers=header)

                assert response.status_code == 400

    def test_updateUserReturnsErrorWhenUpdateUserRaisesException(self, mockApp):
        mockDB = app_utils.getDB(mockApp)
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
            with mockApp.test_client() as client:
                response = client.patch(url, json=userProperties)

                assert response.status_code == e.getStatusCode()

    def test_deleteUserReturns200(self, mockApp):
        mockDB = app_utils.getDB(mockApp)
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200

            assert mockDB.deleteUser.call_count == 1
            arg1Passed = mockDB.deleteUser.call_args[0][0]
            assert arg1Passed == [userIdToDelete]

    def test_deleteUserReturnsErrorWhenDeleteUserRaisesException(self, mockApp):
        mockDB = app_utils.getDB(mockApp)
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'
        exceptionsToTest = [
            exceptions.RecordNotFoundError('some error'),
            exceptions.ServerMiscError('some error'),
        ]

        for e in exceptionsToTest:
            mockDB.deleteUser.side_effect = e
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()