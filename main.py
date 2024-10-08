"""
Using Imgur as free cloud storage
"""
import sys
from alive_progress import alive_bar

import modules.logger as logs
from modules.database import DataBase
from modules.filereader import FileReader
from modules.imagewriter import FileWriter


logger = logs.Logger()
db = DataBase(logger)
filereader = FileReader(logger)
filewriter = FileWriter(logger)

logger.log('Starting main process')
try:
    if len(sys.argv) <= 1:
        raise ValueError('No file specified.')
    # Collect settings:
    calling_args = sys.argv[1:]
    filenames = []
    color_mode = 'L'
    skip_next = False
    for i, arg in enumerate(calling_args):
        if skip_next:
            skip_next = False
            continue
        if arg in ('-m', '--mode'):
            color_mode = calling_args[i + 1]
            skip_next = True
        else:
            filenames.append(arg)

    with alive_bar(len(filenames)) as abar:
        for input_filename in filenames:
            abar()
            logger.log(f'Working on {input_filename}...')

            # Reading input file
            input_file_data = filereader.read(input_filename)

            # getting filename like this is not the best but who cares
            new_filename = input_filename.split('.')[0]
            # Writing image
            image_file = filewriter.write(
                byte_data=input_file_data,
                filename=new_filename,
                mode=color_mode,
            )
except Exception as e:
    logger.log('An error occurred while running:', status=logs.FATAL)
    logger.log(f'{e}', status=logs.FATAL)
finally:
    db.close()
    logger.close()
