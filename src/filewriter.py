"""
File writing module
"""
import uuid
from PIL import Image, ImageDraw

import src.logger as logs


class FileWriter():
    """
    File writer class
    """
    logger = None
    def __init__(self, logger: logs.Logger) -> None:
        self.logger = logger
        self.logger.log('FileWriter ready')

    def write(self, data: bytes, filename) -> None:
        """
        Writes passed bytes data. File is saved with passed name.
        """
        pass
