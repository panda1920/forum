import sys
import pytest
import json
from pathlib import Path
from flask import request, current_app
from unittest.mock import create_autospec

PROJECT_DIR = Path(__file__).resolve().parents[2]

sys.path.append( str(PROJECT_DIR / 'server') )
sys.path.append( str(PROJECT_DIR / 'mongodb') )
import server
from mongodb import MongoDB

@pytest.fixture(scope='function')
def app():
    app = server.setupApp()
    
    # make sure exceptions propagate to the test client
    app.testing = True

    # replace database with mock
    app.config['DATABASE_OBJECT'] = create_autospec(MongoDB)

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

    def test_post_callsStorePostOnDB(self, app):
        jsonData = {
            'author': 'someone',
            'message': 'Hello world'
        }
        db = app.config['DATABASE_OBJECT']

        with app.test_client() as client:
            client.post('/api/post', json=jsonData)

            assert db.storePost.call_count == 1

    def test_post_ifDBThrowsErrorReturn500(self, app):
        jsonData = {
            'author': 'someone',
            'message': 'Hello world'
        }
        db = app.config['DATABASE_OBJECT']
        db.storePost.side_effect = Exception('Went wrong')

        with app.test_client() as client:
            rv = client.post('/api/post', json=jsonData)

            assert rv.status_code == 500