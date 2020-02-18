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
            binary(bytes) 
        Returns:
            return value
        """
        raise NotImplementedError

class AWSFileRepository(FileRepository):
    """
    Uses AWS S3 as file repository.
    Provides interface to access resources in S3.
    """

    def __init__(self, bucket_name):
        self._bucket_name = bucket_name
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

    def _createS3Client(self):
        with self._awsOperationHandler('Failed to connect to repo'):
            return boto3.client('s3',
                aws_access_key_id= self._access_key,
                aws_secret_access_key= self._secret_key,
            )

    @contextmanager
    def _awsOperationHandler(self, errorMsg):
        try:
            yield
        except Exception as e:
            logging.error(e)
            raise exceptions.FailedAWSOperation(errorMsg)