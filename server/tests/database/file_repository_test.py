# -*- coding: utf-8 -*-
"""
This file houses tests for file_repository.py
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import boto3

from server.database.file_repository import AWSFileRepository
import server.exceptions as exceptions

ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
TEST_BUCKETNAME = 'myforumapp-test-bucket'
TEST_DATA_PATH = Path(__file__).parents[0] / 'testdata.json'
DEFAULT_TEST_FILENAME='filename.txt'

@pytest.fixture(scope='module', autouse=True)
def setupS3Bucket():
    s3 = createS3Client()
    try:
        s3.create_bucket(
            Bucket=TEST_BUCKETNAME,
            CreateBucketConfiguration=dict(
                LocationConstraint=DEFAULT_REGION
            )
        )
    except:
        pass

    yield

    s3.delete_bucket(
        Bucket=TEST_BUCKETNAME
    )
    
@pytest.fixture(scope='function')
def cleanupS3Bucket():
    yield
    s3 = createS3Client()
    objects = retrieveS3Objects(s3)
    deleteS3Objects(s3, objects)

@pytest.fixture(scope='function')
def putSampleFile():
    s3 = createS3Client()
    with TEST_DATA_PATH.open('rb') as data:
        s3.upload_fileobj(data, TEST_BUCKETNAME, DEFAULT_TEST_FILENAME)

def createS3Client():
    return boto3.client('s3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

def retrieveS3Objects(s3):
    response = s3.list_objects_v2(
        Bucket=TEST_BUCKETNAME,
    )
    try:
        return response['Contents']
    except:
        return []

def deleteS3Objects(s3, objects):
    objectKeys = [ dict(Key=obj['Key']) for obj in objects ]
    s3.delete_objects(
        Bucket=TEST_BUCKETNAME,
        Delete=dict(Objects=objectKeys)
    )

@pytest.mark.integration
class TestAWSFileRepository:
    # test file search
    # test case where file search yields no result
    # test case where file search yields multiple results
    # test case where file search fails
    # test delete file
    
    def test_writeBinaryCreatesFileInRepo(self, cleanupS3Bucket):
        with TEST_DATA_PATH.open('rb') as fp:
            binary = fp.read()
        s3 = createS3Client()
        test_filename = DEFAULT_TEST_FILENAME
        repo = AWSFileRepository(TEST_BUCKETNAME)

        assert len(retrieveS3Objects(s3)) == 0
        
        repo.writeBinary(binary, test_filename)

        objects = retrieveS3Objects(s3)
        assert len(objects) == 1
        assert objects[0]['Key'] == test_filename

    def test_writeBinaryFilenameWithSlashesCreatesFileInRepo(self, cleanupS3Bucket):
        with TEST_DATA_PATH.open('rb') as fp:
            binary = fp.read()
        s3 = createS3Client()
        test_filename='path/to/file/name.txt'
        repo = AWSFileRepository(TEST_BUCKETNAME)

        assert len(retrieveS3Objects(s3)) == 0
        
        repo.writeBinary(binary, test_filename)

        objects = retrieveS3Objects(s3)
        assert len(objects) == 1
        assert objects[0]['Key'] == test_filename

    def test_writeBinaryRaisesExceptionWhenWriteFailes(self):
        with TEST_DATA_PATH.open('rb') as fp:
            binary = fp.read()
        s3 = createS3Client()
        test_filename='filename.txt'
        repo = AWSFileRepository(TEST_BUCKETNAME)

        # setup mocks
        mock_s3client = MagicMock()
        mock_putobject = MagicMock()
        mock_s3client.return_value=mock_putobject
        mock_putobject.put_object.side_effect = Exception('Some Exception')

        with patch('boto3.client', new=mock_s3client), pytest.raises(exceptions.FailedAWSOperation):
            
            repo.writeBinary(binary, test_filename)

    def test_writeBinaryOverwritesFileThatExist(self, putSampleFile, cleanupS3Bucket):
        binary = bytes([1, 1, 1, 1])
        s3 = createS3Client()
        test_filename = DEFAULT_TEST_FILENAME
        repo = AWSFileRepository(TEST_BUCKETNAME)

        assert len(retrieveS3Objects(s3)) == 1
        
        repo.writeBinary(binary, test_filename)

        objects = retrieveS3Objects(s3)
        assert len(objects) == 1
        assert objects[0]['Key'] == test_filename
        assert objects[0]['Size'] == 4