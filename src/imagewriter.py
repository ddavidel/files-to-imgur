"""
File writing module
"""
import io
import uuid
import math
from PIL import Image

import src.logger as logs


class FileWriter():
    """
    File writer class
    """
    logger = None
    def __init__(self, logger: logs.Logger) -> None:
        self.logger = logger
        self.logger.log('FileWriter ready')

    def write(
            self,
            byte_data: bytes,
            filename: str,
            img_format: str = 'jpg',
            mode: str = 'L'
        ) -> str:
        """
        Writes passed bytes data as an image. File is saved with passed name.
        """
        output_path = f'{filename}.{img_format}'

        # Determine the number of bytes
        num_bytes = len(byte_data)

        # Find dimensions as close to square as possible
        side_length = int(math.sqrt(num_bytes))
        width = height = side_length

        # Adjust for different modes
        if mode == 'RGB':
            bytes_per_pixel = 3
        elif mode == 'L':
            bytes_per_pixel = 1
        else:
            raise ValueError("Unsupported mode. Use 'L' for grayscale or 'RGB' for color.")

        # Calculate the total number of pixels needed
        total_pixels = width * height
        required_bytes = total_pixels * bytes_per_pixel

        # If there are too few bytes, pad with zeroes
        if num_bytes < required_bytes:
            byte_data += b'\x00' * (required_bytes - num_bytes)
        # If there are too many bytes, trim the excess
        elif num_bytes > required_bytes:
            byte_data = byte_data[:required_bytes]

        # Create the image
        image = Image.frombytes(mode, (width, height), byte_data)

        # Save the image to the output path
        image.save(output_path)
        self.logger.log(f"Image saved to {output_path}")

        return output_path
