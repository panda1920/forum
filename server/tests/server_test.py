import sys
import pytest
import json
import urllib.parse
from pathlib import Path
from flask import request, current_app
from unittest.mock import create_autospec

PROJECT_DIR = Path(__file__).resolve().parents[2]

sys.path.append( str(PROJECT_DIR / 'server') )
import server
from database.database import Database

@pytest.fixture(scope='function')
def app():
    app = server.setupApp()
    
    # make sure exceptions propagate to the test client
    app.testing = True

    # replace database with mock
    app.config['DATABASE_OBJECT'] = create_autospec(Database)

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
        db = app.config['DATABASE_OBJECT']
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
            'post': 'This is a post by 112233 for test'
        })

        with app.test_client() as client:
            response = client.post('/api/post', data=formData)

            assert request.form == {}
            assert response.status_code == 500

    def test_postCallsCreatePostOnDB(self, app):
        formData = urllib.parse.urlencode({
            'userId': '112233',
            'post': 'This is a post by 112233 for test'
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }

        with app.test_client() as client:
            response = client.post('/api/post', data=formData, headers=header)
            assert response.status_code == 200
            
            mockDB = app.config['DATABASE_OBJECT']
            assert mockDB.createPost.call_count == 1

            passedPost = mockDB.createPost.call_args[0][0]
            assert passedPost['userId'] == '112233'
            assert passedPost['post'] == 'This is a post by 112233 for test'
            assert 'postId' in passedPost.keys()

    def test_postAPICallsDeletePostOnDBWhenDELETE(self, app):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }
        
        with app.test_client() as client:
            response = client.delete('/api/post', data=formData, headers=header)
            assert response.status_code == 200

            mockDB = app.config['DATABASE_OBJECT']
            assert mockDB.deletePost.call_count == 1

    def test_postAPICallsSearchPostOnDBWhenGET(self, app):
        searchCriteria = {
            'postId': '0',
        }

        with app.test_client() as client:
            response = client.get('/api/post', query_string=searchCriteria)
            assert response.status_code == 200

            mockDB = app.config['DATABASE_OBJECT']
            assert mockDB.searchPost.call_count == 1

    def test_postAPICallsUpdatePostOnDBWhenPATCH(self, app):
        formData = urllib.parse.urlencode({
            'postId': '0',
        })
        header = { 'content-type': 'application/x-www-form-urlencoded' }
        
        with app.test_client() as client:
            response = client.patch('/api/post', data=formData, headers=header)
            assert response.status_code == 200
            
            # mockDB = app.config['DATABASE_OBJECT']
            # assert mockDB.updatePost.call_count == 1