import json
import urllib.parse
import pytest
from flask import request

import tests.mocks as mocks
from server.config import Config
import server.exceptions as exceptions

DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES = 'some_value'
DEFAULT_RETURN_CREATENEWPOST = None
DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES = 'some_value'
DEFAULT_RETURN_SIGNUP = None


@pytest.fixture(scope='function')
def mockApp(app):
    # replace with mock
    mockDB = mocks.createMockDB()
    app.config['DATABASE_REPOSITORY'] = mockDB

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
        db = Config.getDB(mockApp)
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
        
        mockDB = Config.getDB(mockApp)
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

        mockDB = Config.getDB(mockApp)
        assert mockDB.deletePost.call_count == 1

    def test_postAPICallsSearchPostOnDBWhenGET(self, mockApp, client):
        searchCriteria = {
            'postId': '0',
        }

        response = client.get('/api/post', query_string=searchCriteria)
        assert response.status_code == 200

        mockDB = Config.getDB(mockApp)
        assert mockDB.searchPost.call_count == 1

    def test_postAPICallsUpdatePostOnDBWhenPATCH(self, mockApp, client):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'Content-Type': 'application/x-www-form-urlencoded' }
        
        response = client.patch('/api/post', data=formData, headers=header)
        assert response.status_code == 200
            
            # mockDB = Config.getDB(mockApp)
            # assert mockDB.updatePost.call_count == 1

    def test_userlistReturnsAllUsers(self, mockApp, client):
        users = [{'userName': '1'}, {'userName': '2'}]
        mockDB = Config.getDB(mockApp)
        mockDB.searchUser.return_value = users

        response = client.get('/userlist')
        assert response.status_code == 200
        jsonBody = response.get_json()
        assert jsonBody['users'] == users


class TestPostAPIs:
    POSTSAPI_BASE_URL = '/v1/posts'

    def test_searchPostsAPIPassesQueryStringToSearchService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(keyValues)

    def test_searchPostsAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        keyValues = dict(
            search='1 2 3 4',
        )

        with mockApp.test_client() as client:
            response = client.get(self.POSTSAPI_BASE_URL, query_string=keyValues)

            assert response.status_code == 200
            jsonResponse = response.get_json()
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES

    def test_searchPostsReturnsErrorWhenExceptionWasRaised(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
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
        mockSearch = Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            client.get(url)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def searchPostsByIdAPIIgnoresQueryString(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        keyValues = dict(offset=30, limit=100)

        with mockApp.test_client() as client:
            client.get(url, query_string=keyValues)

            mockSearch.searchPostsByKeyValues.assert_called_with(dict(
                postId=postId
            ))

    def test_searchPostsByIdAPIReturns200AndWhatsReturnedFromService(self, mockApp):
        Config.getSearchService(mockApp)
        postId = '11223344'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200
            jsonResponse = response.get_json()
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHPOSTSBYKEYVALUES

    def test_searchPostsByIdAPIReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
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
        mockCreate = Config.getCreationService(mockApp)
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
        mockCreate = Config.getCreationService(mockApp)
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
        mockCreate = Config.getCreationService(mockApp)
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
        mockDB = Config.getDB(mockApp)
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
        mockDB = Config.getDB(mockApp)
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
            Config.getDB(mockApp).updatePost.side_effect = e
            with mockApp.test_client() as client:
                response = client.patch(url, json=updateData)

                assert response.status_code == e.getStatusCode()

    def test_deletePostReturns200(self, mockApp):
        postIdToDelete = '1'
        url = f'{self.POSTSAPI_BASE_URL}/{postIdToDelete}/delete'
        mockDB = Config.getDB(mockApp)

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
        mockDB = Config.getDB(mockApp)

        for e in exceptionsToTest:
            mockDB.deletePost.side_effect = e
            with mockApp.test_client() as client:
                response = client.delete(url)

                assert response.status_code == e.getStatusCode()

class TestUserAPIs:
    USERAPI_BASE_URL = '/v1/users'

    def test_searchUsersPassesQueryStringToService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='username'
        )

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=keyValues)

            mockSearch.searchUsersByKeyValues.assert_called_with(keyValues)

    def test_searchUsersReturns200AearchResultFromService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='username'
        )

        with mockApp.test_client() as client:
            response = client.get(self.USERAPI_BASE_URL, query_string=keyValues)
            jsonResponse =  response.get_json()

            assert response.status_code == 200
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES
        
    def test_searchUsersReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        keyValues = dict(
            search='username'
        )
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError,
            exceptions.InvalidFilterOperatorError,
        ]

        for e in exceptionsToTest:
            mockSearch.searchUsersByKeyValues.side_effect = e()
            with mockApp.test_client() as client:
                response = client.get(self.USERAPI_BASE_URL, query_string=keyValues)

                assert response.status_code == e.getStatusCode()

    def test_searchUserByExplicitIDPassesUserIdToService(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            response = client.get(url)

            mockSearch.searchUsersByKeyValues.assert_called_with(dict(userId=userId))

    def test_searchUserByExplicitIDIgnoresQueryString(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'
        keyValues=dict(offset=30, limit=100)

        with mockApp.test_client() as client:
            response = client.get(url, query_string=keyValues)

            mockSearch.searchUsersByKeyValues.assert_called_with(dict(userId=userId))

    def test_searchUserByExplicitIDReturns200AndSearchResultFromService(self, mockApp):
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'

        with mockApp.test_client() as client:
            response = client.get(url)
            jsonResponse = response.get_json()

            assert response.status_code == 200
            assert jsonResponse['searchResult'] == DEFAULT_RETURN_SEARCHUSERSBYKEYVALUES

    def test_searchUserByExplicitIDReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockSearch = Config.getSearchService(mockApp)
        userId = '11111111'
        url = f'{self.USERAPI_BASE_URL}/{userId}'
        exceptionsToTest = [
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError,
            exceptions.InvalidFilterOperatorError,
        ]

        for e in exceptionsToTest:
            mockSearch.searchUsersByKeyValues.side_effect = e()
            with mockApp.test_client() as client:
                response = client.get(url)

                assert response.status_code == e.getStatusCode()

    def test_createUserPassesFormDataToService(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
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

            mockCreate.signup.assert_called_with(userProperties)

    def test_createUserReturns201WhenSuccess(self, mockApp):
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

            assert response.status_code == 201

    def test_createUserReturnsErrorWhenServiceRaisesException(self, mockApp):
        mockCreate = Config.getCreationService(mockApp)
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
            exceptions.FailedMongoOperation,
            exceptions.ServerMiscError,
            exceptions.InvalidFilterOperatorError,
        ]

        for e in exceptionsToTest:
            mockCreate.signup.side_effect = e()
            with mockApp.test_client() as client:
                response = client.post(url, data=userProperties, headers=headers)

                assert response.status_code == e.getStatusCode()

    def test_updateUserReturns200(self, mockApp):
        mockDB = Config.getDB(mockApp)
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
        mockDB = Config.getDB(mockApp)
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
        mockDB = Config.getDB(mockApp)
        userIdToDelete = '1'
        url = f'{self.USERAPI_BASE_URL}/{userIdToDelete}/delete'

        with mockApp.test_client() as client:
            response = client.delete(url)

            assert response.status_code == 200

            assert mockDB.deleteUser.call_count == 1
            arg1Passed = mockDB.deleteUser.call_args[0][0]
            assert arg1Passed == [userIdToDelete]

    def test_deleteUserReturnsErrorWhenDeleteUserRaisesException(self, mockApp):
        mockDB = Config.getDB(mockApp)
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