# -*- coding: utf-8 -*-
"""
This file houses tests for portrait_uploader.py
"""
import pytest
from pathlib import Path

from server.services.portrait_uploader import PortraitUploader
from tests.helpers import create_mock_entity_fromattrs, create_testuser_attrs
import tests.mocks as mocks
import server.exceptions as exceptions


TESTDATA_PATH = Path(__file__).resolve().parents[1] / 'testdata'
DEFAULT_IMAGE = TESTDATA_PATH / 'sample_image.png'
DEFAULT_URL = 'https://www.example.com/test_binary_file'
DEFAULT_USERNAME = 'test_user@example.com'
DEFAULT_USER_ATTRS = create_testuser_attrs(
    userName=DEFAULT_USERNAME
)
DEFAULT_USER = create_mock_entity_fromattrs(DEFAULT_USER_ATTRS)


@pytest.fixture(scope='function')
def uploader():
    mock_session = mocks.createMockSessionService()
    mock_session.get_user.return_value = DEFAULT_USER

    mock_file_repo = mocks.createMockFileRepository()
    mock_file_repo.getUrl.return_value = DEFAULT_URL

    return PortraitUploader(mock_session, mock_file_repo)


class TestPortraitUploader:
    def test_uploadShouldPassBinaryToFileRepo(self, uploader):
        mock_file_repo = uploader._file_repo
        with DEFAULT_IMAGE.open('rb') as f:
            data = f.read()

        uploader.upload(data)

        assert mock_file_repo.writeBinary.call_count == 1
        binary, *_ = mock_file_repo.writeBinary.call_args_list[0][0]
        assert binary == data

    def test_uploadShouldCreateFilenameFromUsername(self, uploader):
        mock_file_repo = uploader._file_repo
        with DEFAULT_IMAGE.open('rb') as f:
            data = f.read()
        expected_filename = f'portraits/{DEFAULT_USERNAME}.png'

        uploader.upload(data)

        _, filename = mock_file_repo.writeBinary.call_args_list[0][0]
        assert filename == expected_filename

    def test_uploadShouldReturnPublicUrlOfFile(self, uploader):
        mock_file_repo = uploader._file_repo
        with DEFAULT_IMAGE.open('rb') as f:
            data = f.read()

        response = uploader.upload(data)

        assert response['publicUrl'] == DEFAULT_URL
        assert mock_file_repo.getUrl.call_count == 1

    def test_uploadShouldRaiseExceptionWhenBinaryIsNotImage(self, uploader):
        FAKE_IMAGE_DATA = b'hello this is some random bytes'

        with pytest.raises(exceptions.InvalidImageFileError):
            uploader.upload(FAKE_IMAGE_DATA)
