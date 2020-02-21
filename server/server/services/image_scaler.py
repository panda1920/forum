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
            image = self._binary_to_image(binary)
            image_format = image.format  # jpeg, png etc;

            resized = image.resize(dimension)
            
            return self._image_to_binary(resized, image_format)
        
        except UnidentifiedImageError as e:
            logging.error(e)
            raise exceptions.InvalidImageFileError('Invalid image file')
        
        except Exception as e:
            logging.error(e)
            raise exceptions.ServerMiscError('Failed image resize')

    def _binary_to_image(self, binary):
        """
        converts binary bytes to PIL image
        
        Args:
            binary(bytes): binary of image
        Returns:
            PIL image
        """
        return Image.open( io.BytesIO(binary) )

    def _image_to_binary(self, image, image_format):
        """
        converts PIL image to binary bytes
        
        Args:
            image: PIL image
            image_format: desired format of output binary; jpeg, png etc.
        Returns:
            Bytes
        """
        binary_stream = io.BytesIO()
        image.save(binary_stream, image_format)
        return binary_stream.getvalue()
