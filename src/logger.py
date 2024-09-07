"""
Logger
"""
from datetime import datetime

INFO = 1
WARNING = 2
ERROR = 3
FATAL = -1


STATUS_DICT = {
    -1: '[FATAL]:',
    1: '[INFO]:',
    2: '[WARNING]:',
    3: '[ERROR]:',
}


class Logger():
    """
    Logs what happens
    """
    logfile_name = ''
    logfile = None

    def __init__(self) -> None:
        self.logfile_name = f'log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt'
        self.logfile = open(f'logs/{self.logfile_name}', 'wt', encoding='utf-8')
        self.log('Logger started', INFO)

    def _post_write(self) -> None:
        """
        Post write actions
        """
        self.logfile.flush()

    def log(self, message: str, status: int = 1) -> None:
        """
        Writes passed message into current log file
        """
        self.logfile.write(f'{STATUS_DICT.get(status)} {message}\n')
        self._post_write()

    def close(self) -> None:
        """
        Closes the log file
        """
        self.log('Closing logger... Bye Bye')
        self.logfile.close()
