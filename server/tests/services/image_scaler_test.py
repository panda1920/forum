# -*- coding: utf-8 -*-
"""
This file houses tests for image_scaler.py
"""

import io
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from server.services.image_scaler import ImageScaler
import server.exceptions as exceptions

TESTDATA_PATH = Path(__file__).resolve().parents[0] / 'testdata'
TEMPORARY_STORAGE = TESTDATA_PATH / 'temp'
IMAGE_01 = TESTDATA_PATH / 'test_image01.jpeg'
IMAGE_02 = TESTDATA_PATH / 'test_image02.png'
NON_IMAGE = TESTDATA_PATH / 'some_text01.txt'


@pytest.fixture(scope='function')
def cleanup_temp():
    shutil.rmtree(TEMPORARY_STORAGE, ignore_errors=True)
    TEMPORARY_STORAGE.mkdir(exist_ok=True)


class TestImageScaler:
    def test_resizeBinaryShouldResizeJpegImageToSpecifiedDimension(self, cleanup_temp):
        with IMAGE_01.open('rb') as fp:
            binary = fp.read()
        dimensions = [
            (1000, 1000),
            (250, 250),
            (144, 100),
            (1, 1),
        ]
        imagescaler = ImageScaler()

        for dimension in dimensions:
            resized = imagescaler.resize_image_binary(binary, dimension)
            image = Image.open( io.BytesIO(resized) )

            assert image.size == dimension

    def test_resizeBinaryShouldResizePngImageToSpecifiedDimension(self, cleanup_temp):
        with IMAGE_02.open('rb') as fp:
            binary = fp.read()
        dimensions = [
            (1000, 1000),
            (250, 250),
            (144, 100),
            (1, 1),
        ]
        imagescaler = ImageScaler()

        for dimension in dimensions:
            resized = imagescaler.resize_image_binary(binary, dimension)
            image = Image.open( io.BytesIO(resized) )

            assert image.size == dimension

    def test_reiszeBinaryShouldRaiseExceptionWhenBinaryofNonImagePassed(self, cleanup_temp):
        with NON_IMAGE.open('rb') as fp:
            binary = fp.read()
        dimension = (20, 20)
        imagescaler = ImageScaler()

        with pytest.raises(exceptions.InvalidImageFileError):
            imagescaler.resize_image_binary(binary, dimension)

    def test_resizeBinaryShouldRaiseExceptionWhenExecutionFailed(self, cleanup_temp):
        with IMAGE_01.open('rb') as fp:
            binary = fp.read()
        dimension = (20, 20)
        imagescaler = ImageScaler()

        # setup mock
        image_mock = MagicMock()
        opened_mock = MagicMock()
        opened_mock.resize.side_effect = Exception('Some error')
        image_mock.open.return_value = opened_mock

        with pytest.raises(exceptions.ServerMiscError):
            with patch('server.services.image_scaler.Image', new=image_mock):
                imagescaler.resize_image_binary(binary, dimension)
