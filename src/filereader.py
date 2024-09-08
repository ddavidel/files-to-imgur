"""
File reading module
"""
import sys
import src.logger as logs

class FileReader():
    """
    File reader class
    """
    logger = None
    def __init__(self, logger: logs.Logger) -> None:
        self.logger = logger
        self.logger.log('FileReader ready')

    def read(self, filename: str) -> bytes:
        """
        Opens passed file in 'rb' mode.
        Returns data as bytes
        """
        # print(f'Reading file {filename}... This could take a while')
        self.logger.log(f'Reading file {filename}...')
        data = bytes()
        try:
            with open(filename, 'rb') as input_file_bytes:
                while True:
                    cur_line = input_file_bytes.readline()
                    if cur_line:
                        data = data + cur_line
                    else:
                        input_file_bytes.close()
                        break
        except Exception as e:
            self.logger.log(f'Fatal error while reading file {filename}: {e}', status=logs.FATAL)
            print(f'An error occurred while reading {filename}. See {self.logger.logfile_name} for more')
            sys.exit()

        # print('Reading completed.')
        self.logger.log(f'Reading of file {filename} completed')
        return data
