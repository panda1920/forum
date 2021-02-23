# -*- coding: utf-8 -*-
"""
This file houses class to upload portrait picture of users
"""
import io
from contextlib import contextmanager

from PIL import Image

import server.exceptions as exceptions


class PortraitUploader:
    def __init__(self, session, file_repo):
        self._session = session
        self._file_repo = file_repo
        self._image_path = 'portraits'

    def upload(self, binary):
        """
        Uploads portrait image
        
        Args:
            binary - byte sequence of the image
        Returns:
            None
        """
        with self._errorHandler('Invalid image format'):
            image = Image.open( io.BytesIO(binary) )
        filename = self._create_filename(image)

        self._file_repo.writeBinary(binary, filename)

        public_url = self._file_repo.getUrl(filename)
        return dict(
            publicUrl=public_url
        )

    def _create_filename(self, image):
        filename = self._session.get_user().userName
        extension = image.format.lower()

        return f'{self._image_path}/{filename}.{extension}'

    @contextmanager
    def _errorHandler(self, msg):
        try:
            yield
        except Exception:
            raise exceptions.InvalidImageFileError(msg)
