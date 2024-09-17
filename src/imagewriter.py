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

        num_bytes = len(byte_data)

        side_length = int(math.sqrt(num_bytes))
        width = height = side_length

        if mode == 'RGB':
            bytes_per_pixel = 3
        elif mode == 'L':
            bytes_per_pixel = 1
        else:
            raise ValueError("Unsupported mode. Use 'L' for grayscale or 'RGB' for color.")

        total_pixels = width * height
        required_bytes = total_pixels * bytes_per_pixel

        if num_bytes < required_bytes:
            byte_data += b'\x00' * (required_bytes - num_bytes)
        elif num_bytes > required_bytes:
            byte_data = byte_data[:required_bytes]

        image = Image.frombytes(mode, (width, height), byte_data)

        image.save(output_path)
        self.logger.log(f"Image saved to {output_path}")

        return output_path
