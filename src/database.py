"""
module responsible of managing the 'db'


FIXME:
this need a non indifferent overhaul.
Writer and Reader should have the same objects as a superclass, not only the class
This allows to open the file in 'r+' mode that allows to read and write without truncating
and this also prevents buffering issues due to opening the same file multiple times
THIS NEEDS TO BE FIXED AS SOON AS POSSIBLE
"""
import os
import ast
import src.logger as logs


DATABASE_NAME = "defaultdb.ddevdb"


# This is mainly used as a template by me, and for validation by the worker
# Keep in mind that ddevdb can store anything, even if it's not defined here
# Now that i think of it, it makes this useless as a validation...
DB_OBJECT_TYPES = {
    'converted_image': {
        'items_number': 4,
        'filename': '',
        'format': '',
        'url': '',
    }
}


class DBWorker():
    """
    DB Worker. This is the base class for any or most db workers.
    It includes useful methods and much more
    """
    dbname = ''
    dbfile = None
    logger = None
    dbkey = ''
    worker_mode = ''

    def __init__(self, dbname: str, logger: logs.Logger, worker_mode: str) -> None:
        self.dbname = dbname
        if not os.path.isfile(dbname):
            logger.log(f'Creating DB file with name {dbname}...', logs.INFO)
        self.logger = logger
        self.dbfile = open(dbname, worker_mode, encoding="utf-8")
        self.dbkey = dbname # atm key is dbname, will be changed
        self.worker_mode = worker_mode

    def _post_write(self) -> None:
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

    def validate_row(self, row: dict) -> str:
        """
        Checks passed db row following ddevdb standards.
        Passed row has to be decoded
        """
        errors = []

        if not row:
            errors.append('Empty row in validation')

        # Work in progress...

        return errors

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

        return ast.literal_eval(''.join(result))

    def reset_db_connection(self) -> None:
        """
        Restarts the connection with the current db
        """
        self.dbfile.close()
        self.dbfile = open(self.dbname, self.worker_mode, encoding="utf-8")

class Writer(DBWorker):
    """
    Class responsible for writing data to the db
    """
    def __init__(self, dbname: str, logger: logs.Logger) -> None:
        super().__init__(dbname, logger, 'w')
        self.logger.log('DB Writer ready', logs.INFO)

    def close(self) -> None:
        """
        Closes the Writer
        """
        self.logger.log('Closing Writer...')
        error = self.close_worker()
        self.logger.log(
            'Error while closing DB Writer' if error else 'Writer closed',
            status=logs.ERROR if error else logs.INFO
        )

    def encode(self, row: str) -> str:
        """
        Encode passed row
        """
        return super().encode_decode(row)

    def write_to_db(
            self,
            rows: list,
        ) -> None:
        """
        Writes data into db
        
        :params rows: List of ddevdb standardized dicts
        """
        self.logger.log(f"Writing {len(rows)} into db...")

        for row in rows:
            self.dbfile.write(row)

    def _ping_reader(self, idk):
        """
        This function will send newly added data to the reader so he
        is up to date, without needing to re-read all the db
        """


class Reader(DBWorker):
    """
    Class responsible for reading data from the db
    """
    data = {}

    def __init__(self, dbname: str, logger: logs.Logger) -> None:
        super().__init__(dbname, logger, 'r+')
        self.data = self._read_from_db()
        self.logger.log('DB Reader ready', logs.INFO)

    def decode(self, row: str) -> str:
        """
        Decode passed row
        """
        return super().encode_decode(row)

    def close(self) -> None:
        """
        Closes the Reader
        """
        self.logger.log('Closing Reader...')
        error = self.close_worker()
        self.logger.log(
            'Error while closing DB Reader' if error else 'Reader closed',
            status=logs.ERROR if error else logs.INFO
        )

    def _read_from_db(self) -> dict:
        """
        This function will filter db items returning a list of objects
        and is executed as soon as the reader is loaded (during the init)
        """
        records = self.dbfile.readlines()
        self.reset_db_connection()

        objects = {}
        for id, row in enumerate(records):
            row_obj = self.decode(row)
            objects[id] = row_obj

        return objects

    def lookup(self, what) -> dict:
        """
        This function should look in the data for the what
        and return it as a list/dict (probably list, to be decided)
        """
        # ...do something...


class DataBase():
    """
    This class is the main window the interact with a ddevdb pseudo database

    devdb
    -----
    ddevdb is a pseudo database created by me. It's just a file used by
    this code to write stuff to be saved for the next time.
    
    Instructions
    ------------
    Each row is a record (like on SQL), information is stored on the row. Since there isn't
    a concept of columns, a row can be as long as it can and have as many 'columns'.
    Each row is a python dict object: upon reading from the db, the worker builds
    an actual dict object from the string row.
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
