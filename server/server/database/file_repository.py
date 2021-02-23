# -*- coding: utf-8 -*-
"""
This file houses repository for file storage
"""

import os
import logging
from contextlib import contextmanager

import boto3

import server.exceptions as exceptions


class FileRepository:
    def writeBinary(self, binary, filename):
        """
        Writes binary as file in persistant storage

        Args:
            binary(bytes): data to send
            filename(string): name of the file to create on repository
        Returns:
            None
        """
        raise NotImplementedError

    def searchFiles(self, searchFilter):
        """
        Searches for files in repository
        
        Args:
            searchFilter(Filter): criteria to filter retrieved file infos
        Returns:
            list of file infos
        """
        raise NotImplementedError

    def deleteFiles(self, filenames):
        """
        Delete files from repository
        
        Args:
            filenames(list): list of filenames to delete
        Returns:
            None
        """
        raise NotImplementedError

    def getUrl(self, filename):
        """
        Get url of file stored remotely
        
        Args:
            filename(str): filename to search for
        Returns:
            url string
        """
        raise NotImplementedError


class S3FileRepository(FileRepository):
    """
    Uses AWS S3 as file repository.
    Provides interface to access resources in S3.
    """

    def __init__(self, bucket_name):
        self._bucket_name = bucket_name
        self._bucket_location = None
        self._access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self._secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    def writeBinary(self, binary, filename):
        s3 = self._createS3Client()
        with self._awsOperationHandler('Failed to save file'):
            s3.put_object(
                ACL='public-read',
                Body=binary,
                Bucket=self._bucket_name,
                Key=filename
            )

    def searchFiles(self, searchFilter):
        s3 = self._createS3Client()
        with self._awsOperationHandler('Failed to read from repo'):
            response = s3.list_objects_v2(
                Bucket=self._bucket_name,
            )

        try:
            return [
                file_info for file_info in response['Contents']
                if searchFilter.matches(file_info)
            ]
        except Exception as e:
            logging.error(e)
            return []

    def deleteFiles(self, filenames):
        s3 = self._createS3Client()
        objects_to_delete = dict(Objects=[
            dict(Key=filename) for filename in filenames
        ])

        with self._awsOperationHandler('Failed to delete file in repo'):
            s3.delete_objects(Bucket=self._bucket_name, Delete=objects_to_delete)

    def getUrl(self, filename):
        self._set_bucket_location()

        return f'https://s3-{self._bucket_location}.amazonaws.com/{self._bucket_name}/' + filename

    def _createS3Client(self):
        """
        create client object to communicate with amazon s3
        """
        with self._awsOperationHandler('Failed to connect to repo'):
            return boto3.client(
                's3',
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
            )

    def _set_bucket_location(self):
        if self._bucket_location is not None:
            return

        s3 = self._createS3Client()
        with self._awsOperationHandler('Failed to get bucket info'):
            response = s3.get_bucket_location(Bucket=self._bucket_name)
            self._bucket_location = response['LocationConstraint']

    @contextmanager
    def _awsOperationHandler(self, errorMsg):
        """
        Use this in the with clause to handle aws operations
        Can avoid having to repeatedly type out try-except clause
        """
        try:
            yield
        except Exception as e:
            logging.error(e)
            raise exceptions.FailedAWSOperation(errorMsg)
