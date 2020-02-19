# -*- coding: utf-8 -*-
"""
This file houses tests for file_repository.py
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import boto3

from server.database.file_repository import S3FileRepository
import server.exceptions as exceptions
from server.database.filter import PrimitiveFilter

ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
TEST_BUCKETNAME = 'myforumapp-test-bucket'
TEST_DATA_PATH = Path(__file__).parents[0] / 'testdata.json'
DEFAULT_TEST_FILENAME = 'filename.txt'
DEFAULT_TEST_FILENAMES = [
    'filename1.txt',
    'filename2.txt',
    'filename3.txt',
]


@pytest.fixture(scope='module', autouse=True)
def setupS3Bucket():
    s3 = createS3Client()
    s3.create_bucket(
        Bucket=TEST_BUCKETNAME,
        CreateBucketConfiguration=dict(
            LocationConstraint=DEFAULT_REGION
        )
    )

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
    writeSampleFileAs(s3, DEFAULT_TEST_FILENAME)


@pytest.fixture(scope='function')
def putMultipleSampleFiles():
    s3 = createS3Client()
    for filename in DEFAULT_TEST_FILENAMES:
        writeSampleFileAs(s3, filename)


def createS3Client():
    return boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )


def retrieveS3Objects(s3):
    response = s3.list_objects_v2(
        Bucket=TEST_BUCKETNAME,
    )
    try:
        return response['Contents']
    except Exception:
        return []


def writeSampleFileAs(s3, filename):
    with TEST_DATA_PATH.open('rb') as data:
        s3.upload_fileobj(data, TEST_BUCKETNAME, filename)


def deleteS3Objects(s3, objects):
    objectKeys = [ dict(Key=obj['Key']) for obj in objects ]
    s3.delete_objects(
        Bucket=TEST_BUCKETNAME,
        Delete=dict(Objects=objectKeys)
    )


@pytest.mark.integration
class TestS3FileRepository:
    def test_writeBinaryCreatesFileInRepo(self, cleanupS3Bucket):
        with TEST_DATA_PATH.open('rb') as fp:
            binary = fp.read()
        s3 = createS3Client()
        test_filename = DEFAULT_TEST_FILENAME
        repo = S3FileRepository(TEST_BUCKETNAME)

        assert len(retrieveS3Objects(s3)) == 0
        
        repo.writeBinary(binary, test_filename)

        objects = retrieveS3Objects(s3)
        assert len(objects) == 1
        assert objects[0]['Key'] == test_filename

    def test_writeBinaryFilenameWithSlashesCreatesFileInRepo(self, cleanupS3Bucket):
        with TEST_DATA_PATH.open('rb') as fp:
            binary = fp.read()
        s3 = createS3Client()
        test_filename = 'path/to/file/name.txt'
        repo = S3FileRepository(TEST_BUCKETNAME)

        assert len(retrieveS3Objects(s3)) == 0
        
        repo.writeBinary(binary, test_filename)

        objects = retrieveS3Objects(s3)
        assert len(objects) == 1
        assert objects[0]['Key'] == test_filename

    def test_writeBinaryRaisesExceptionWhenWriteFailes(self):
        with TEST_DATA_PATH.open('rb') as fp:
            binary = fp.read()
        test_filename = 'filename.txt'
        repo = S3FileRepository(TEST_BUCKETNAME)

        # setup mock
        boto3_mock = MagicMock()
        client_mock = MagicMock()
        boto3_mock.client.return_value = client_mock
        client_mock.put_object.side_effect = Exception('Some error')

        with pytest.raises(exceptions.FailedAWSOperation):
            with patch('server.database.file_repository.boto3', new=boto3_mock):
            
                repo.writeBinary(binary, test_filename)

    def test_writeBinaryOverwritesFileThatExist(self, putSampleFile, cleanupS3Bucket):
        binary = bytes([1, 1, 1, 1])
        s3 = createS3Client()
        test_filename = DEFAULT_TEST_FILENAME
        repo = S3FileRepository(TEST_BUCKETNAME)

        repo.writeBinary(binary, test_filename)

        objects = retrieveS3Objects(s3)
        assert len(objects) == 1
        assert objects[0]['Size'] == 4

    def test_searchFilesShouldReturnAllFiles(self, putMultipleSampleFiles, cleanupS3Bucket):
        searchFilter = PrimitiveFilter.createFilter(dict(
            field='Key',
            operator='fuzzy',
            value=DEFAULT_TEST_FILENAMES
        ))
        repo = S3FileRepository(TEST_BUCKETNAME)

        file_infos = repo.searchFiles(searchFilter)

        assert len(file_infos) == 3

    def test_searchFilesShouldReturnMatchedFiles(self, putMultipleSampleFiles, cleanupS3Bucket):
        searchFilters = [
            PrimitiveFilter.createFilter(
                dict( field='Key', operator='eq', value=[DEFAULT_TEST_FILENAMES[0]] )
            ),
            PrimitiveFilter.createFilter(
                dict( field='Key', operator='eq', value=[DEFAULT_TEST_FILENAMES[1]] )
            ),
            PrimitiveFilter.createFilter(
                dict( field='Key', operator='eq', value=['non_existant_name'] )
            ),
            PrimitiveFilter.createFilter(
                dict( field='Key', operator='fuzzy', value=['filename'] )
            ),
        ]
        expectedReturnCounts = [1, 1, 0, 3]
        repo = S3FileRepository(TEST_BUCKETNAME)

        for searchFilter, expectedFound in zip(searchFilters, expectedReturnCounts):

            file_infos = repo.searchFiles(searchFilter)

            assert len(file_infos) == expectedFound

    def test_searchFilesShouldReturnEmptyListWhenNoFileOnS3(self):
        searchFilter = PrimitiveFilter.createFilter(dict(
            field='Key',
            operator='fuzzy',
            value=DEFAULT_TEST_FILENAMES
        ))
        repo = S3FileRepository(TEST_BUCKETNAME)

        file_infos = repo.searchFiles(searchFilter)

        assert len(file_infos) == 0

    def test_searchFilesShouldRaiseExceptionWhenQueryToS3Fails(
        self, putMultipleSampleFiles, cleanupS3Bucket
    ):
        searchFilter = PrimitiveFilter.createFilter(dict(
            field='Key',
            operator='fuzzy',
            value=DEFAULT_TEST_FILENAMES
        ))
        repo = S3FileRepository(TEST_BUCKETNAME)

        # setup mock
        boto3_mock = MagicMock()
        client_mock = MagicMock()
        boto3_mock.client.return_value = client_mock
        client_mock.list_objects_v2.side_effect = Exception('Some error')

        with pytest.raises(exceptions.FailedAWSOperation):
            with patch('server.database.file_repository.boto3', new=boto3_mock):
            
                repo.searchFiles(searchFilter)

    def test_deleteFileShouldRemoveFileFromRepo(self, putMultipleSampleFiles, cleanupS3Bucket):
        filename_to_delete = DEFAULT_TEST_FILENAMES[0]
        repo = S3FileRepository(TEST_BUCKETNAME)

        repo.deleteFiles( [filename_to_delete] )
        
        file_infos = retrieveS3Objects( createS3Client() )
        assert len(file_infos) == 2
        for file_info in file_infos:
            assert filename_to_delete != file_info['Key']

    def test_deleteFilesShouldRemoveMultipleFileFromRepo(
        self, putMultipleSampleFiles, cleanupS3Bucket
    ):
        repo = S3FileRepository(TEST_BUCKETNAME)

        repo.deleteFiles( DEFAULT_TEST_FILENAMES[0:2] )
        
        file_infos = retrieveS3Objects( createS3Client() )
        assert len(file_infos) == 1

    def test_deleteFilesShouldChangeNothingWhenNonExistantFilename(
        self, putMultipleSampleFiles, cleanupS3Bucket
    ):
        repo = S3FileRepository(TEST_BUCKETNAME)

        repo.deleteFiles( ['nonexistant_filename'] )
        
        file_infos = retrieveS3Objects( createS3Client() )
        assert len(file_infos) == 3

    def test_deleteFilesShouldRaiseExceptionWhenOperationFailed(
        self, putMultipleSampleFiles, cleanupS3Bucket
    ):
        repo = S3FileRepository(TEST_BUCKETNAME)

        # setup mock
        boto3_mock = MagicMock()
        client_mock = MagicMock()
        boto3_mock.client.return_value = client_mock
        client_mock.delete_objects.side_effect = Exception('some exception')

        with pytest.raises(exceptions.FailedAWSOperation):
            with patch('server.database.file_repository.boto3', new=boto3_mock):
                repo.deleteFiles( DEFAULT_TEST_FILENAME[0:1] )
