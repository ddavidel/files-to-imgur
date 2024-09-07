"""
Using Imgur as free cloud storage
"""
import sys

import src.logger as logs
from src.database import DataBase
from src.filereader import FileReader
from src.filewriter import FileWriter


logger = logs.Logger()
db = DataBase(logger)
filereader = FileReader(logger)
filewriter = FileWriter(logger)

if len(sys.argv) <= 1:
    logger.log('No file specified.', status=logs.FATAL)
    sys.exit()

input_filename = sys.argv[1]
logger.log(f'Found filename in args: {input_filename}')

input_file_data = filereader.read(input_filename)

db.close()
logger.close()
