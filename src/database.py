"""
module responsible of managing the 'db'
"""
import os
import src.logger as logs


DATABASE_NAME = 'defaultdb.ddevdb'



class DBWorker():
    """
    DB Worker
    """
    dbname = ''
    dbfilename = ''
    dbfile = None
    logger = None

    def _post_write(self) -> None:
        self.dbfile.flush()

    def _close_worker(self) -> bool:
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


class Writer(DBWorker):
    """
    Class responsible for writing data to the db
    """
    def __init__(self, dbname: str, logger: logs.Logger) -> None:
        self.logger = logger
        if not os.path.isfile(dbname):
            logger.log(f'Creating DB file with name {dbname}...', logs.INFO)
        else:
            logger.log(f'Opening DB with name {dbname}...', logs.INFO)
        self.dbfile = open(dbname, 'wb')

        self.logger.log('DB Writer ready', logs.INFO)

    def close(self) -> None:
        """
        Closes the Writer
        """
        self.logger.log('Closing Writer...')
        error = self._close_worker()
        self.logger.log(
            'Error while closing DB Writer' if error else 'Writer closed',
            status=logs.ERROR if error else logs.INFO
        )


class Reader(DBWorker):
    """
    Class responsible for reading data from the db
    """
    def __init__(self, dbname: str, logger: logs.Logger) -> None:
        self.logger = logger
        self.dbfilename = dbname
        self.dbfile = open(dbname, 'rb')
        self.logger.log('DB Reader ready', logs.INFO)

    def close(self) -> None:
        """
        Closes the Reader
        """
        self.logger.log('Closing Reader...')
        error = self._close_worker()
        self.logger.log(
            'Error while closing DB Reader' if error else 'Reader closed',
            status=logs.ERROR if error else logs.INFO
        )


class DataBase():
    """
    Database handler
    """
    dbname = ''
    writer = None
    reader = None
    logger = None

    def __init__(
        self,
        logger: logs.Logger,
        dbname: str = DATABASE_NAME,
    ) -> None:
        self.logger = logger
        self.logger.log('Initializing db...', logs.INFO)
        self.dbname = dbname
        self.writer = Writer(self.dbname, logger)
        self.reader = Reader(self.dbname, logger)

    def close(self) -> None:
        """
        Closes the DB connections
        """
        self.logger.log('Initiating DB closing procedures...')
        self.reader.close()
        self.writer.close()
