import json
import urllib.parse
import pytest
from flask import request
from unittest.mock import create_autospec

from server import server
from server.database.database import Database
from server.database.filter import Filter
from server.database.paging import Paging

@pytest.fixture(scope='function')
def app():
    app = server.setupApp()
    
    # make sure exceptions propagate to the test client
    app.testing = True

    # replace with mock
    app.config['DATABASE_OBJECT'] = create_autospec(Database)
    app.config['SEARCH_FILTER'] = create_autospec(Filter)
    app.config['PAGING'] = create_autospec(Paging)

    yield app

def getMockDB(app):
    return app.config['DATABASE_OBJECT']

def getMockFilter(app):
    return app.config['SEARCH_FILTER']

def getMockPaging(app):
    return app.config['PAGING']


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
        db = getMockDB(app)
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
            
            mockDB = getMockDB(app)
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

            mockDB = getMockDB(app)
            assert mockDB.deletePost.call_count == 1

    def test_postAPICallsSearchPostOnDBWhenGET(self, app):
        searchCriteria = {
            'postId': '0',
        }

        with app.test_client() as client:
            response = client.get('/api/post', query_string=searchCriteria)
            assert response.status_code == 200

            mockDB = getMockDB(app)
            assert mockDB.searchPost.call_count == 1

    def test_postAPICallsUpdatePostOnDBWhenPATCH(self, app):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }
        
        with app.test_client() as client:
            response = client.patch('/api/post', data=formData, headers=header)
            assert response.status_code == 200
            
            # mockDB = getMockDB(app)
            # assert mockDB.updatePost.call_count == 1

class TestPostsAPI:
    POSTSAPI_BASE_URL = '/v1/posts'

    def test_searchPostsAPI(self, app):
        mockDB = getMockDB(app)
        mockDB.searchPost.return_value = ['post1', 'post2']
        mockFilter = getMockFilter(app)
        mockFilter.createFilter.return_value = 'mockfilter'
        mockPaging = getMockPaging(app)
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

    def test_searchPostsWithExplicitIDReturns1Post(self, app):
        postId = 'aaabbb90'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        mockDB = getMockDB(app)
        mockDB.searchPost.return_value = ['user1']
        mockFilter = getMockFilter(app)
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

    def test_searchPostsWithExplicitNonexistantIDReturnsNothing(self, app):
        postId = 'aaabbb90'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        mockDB = getMockDB(app)
        mockDB.searchPost.return_value = []

        with app.test_client() as client:
            response = client.get(url)

            assert response.status_code == 200

            # returns post
            responseBodyJSON = response.get_json()
            assert responseBodyJSON['posts'] == mockDB.searchPost.return_value

    def test_searchPostsWithExplcitIDThrowsExceptionReturnsError(self, app):
        postId = 'aaabbb90'
        url = f'{self.POSTSAPI_BASE_URL}/{postId}'
        mockDB = getMockDB(app)
        mockDB.searchPost.side_effect = Exception('Exception thrown')

        with app.test_client() as client:
            response = client.get(url)

            assert response.status_code == 400

    def test_createPostReturnCreatedPost(self, app):
        url = f'{self.POSTSAPI_BASE_URL}/create'
        newPostData = {
            'userId': '0',
            'content': 'This is a test post',
        }
        headers = { 'content-type': 'application/x-www-form-urlencoded' }

        mockDB = getMockDB(app)
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

    def test_whenCreatePostThrowExceptionReturns400(self, app):
        url = f'{self.POSTSAPI_BASE_URL}/create'
        newPostData = {
            'userId': '0',
            'content': 'This is a test post',
        }
        headers = { 'content-type': 'application/x-www-form-urlencoded' }

        mockDB = getMockDB(app)
        mockDB.createPost.side_effect = Exception('Some error happened')

        with app.test_client() as client:
            response = client.post(url, data=newPostData, headers=headers)

            assert response.status_code == 400