# -*- coding: utf-8 -*-
"""
This file houses class to manipulate image sizes
"""

import io
import logging

from PIL import Image
from PIL import UnidentifiedImageError

import server.exceptions as exceptions


class ImageScalerBase:
    """
    Base class of ImageScaler
    Sets the interface of ImageScaler
    """

    def resize_image_binary(self, binary, dimension):
        """
        Resizes image to specified dimension
        
        Args:
            binary(bytes): binary of the image
            dimension(tuple): tuple of 2 elements: width, height
        Returns:
            Bytes of new image binary
        """
        raise NotImplementedError


class ImageScaler(ImageScalerBase):
    def resize_image_binary(self, binary, dimension):
        try:
            binary_stream = io.BytesIO(binary)
            image = Image.open(binary_stream)
            imageformat = image.format  # jpeg, png etc;

            resized = image.resize(dimension)
            
            binary_stream.seek(0)
            resized.save(binary_stream, imageformat)
            return binary_stream.getvalue()
        
        except UnidentifiedImageError as e:
            logging.error(e)
            raise exceptions.InvalidImageFileError('Invalid image file')
        
        except Exception as e:
            logging.error(e)
            raise exceptions.ServerMiscError('Failed image resize')
