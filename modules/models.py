"""
Module with base models
"""
import os
import modules.logger as logs


class DBWorker():
    """
    DB Worker. This is the base class for any or most db workers.
    It includes useful methods and much more
    """
    dbname = ''
    dbfile = None
    logger = None
    dbkey = ''
    worker_mode = 'r+'

    def __init__(self, dbname: str, logger: logs.Logger, mode: str) -> None:
        self.dbname = dbname
        self.mode = mode
        if not os.path.isfile(dbname):
            logger.log(f'Creating DB file with name {dbname}...', logs.INFO)
        self.logger = logger
        self.dbfile = open(dbname, self.mode)
        self.dbkey = dbname # atm key is dbname, will be changed

    def _post_write(self) -> None:
        self.logger.log("Flushing...")
        self.dbfile.flush()

    def close_worker(self) -> bool:
        """
        Closes the file, rendering the worker useless
        """
        error = False
        try:
            self.dbfile.close()
        except Exception:
            error = True
            self.logger.log("Worker couldn't close connection with db correctly", status=logs.ERROR)
        return error

    def validate_row(self, row: dict) -> bool:
        """
        Checks passed db row following ddevdb standards.
        Passed row has to be decoded
        Returns true if row is valid otherwise false
        """
        errors = []

        if not row:
            errors.append('Empty row in validation')

        if not isinstance(row, dict):
            errors.append('Invalid row')

        # do more stuff

        for error in errors:
            self.logger.log(
                "The following error occurred while validating row: {}".format(
                    error
                ),
                status=logs.ERROR
            )

        return False if errors else True

    def encode_decode(self, row: str) -> dict:
        """
        Encrypts or decrypts passed row and returs it
        """
        result = []
        key_length = len(self.dbkey)

        # pylint: disable=consider-using-enumerate
        for i in range(len(row)):
            c_char = chr(ord(row[i]) ^ ord(self.dbkey[i % key_length]))
            result.append(c_char)

        return ''.join(result)

    def reset_db_connection(self) -> None:
        """
        Resets the connection from the beginning
        """
        self.dbfile.seek(0)
        self.logger.log('Connection with db reset')

    def restart_db_connection(self) -> None:
        """
        Closes the connection and starts it again
        """
        self.dbfile.close()
        self.dbfile = open(self.dbname, self.worker_mode, encoding="utf-8")
        self.logger.log('Connection with db restarted')
