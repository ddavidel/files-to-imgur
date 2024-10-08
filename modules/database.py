"""
module responsible of managing the 'db'
"""
import os
import ast
import modules.logger as logs
from modules.models import DBWorker


DATABASE_NAME = "defaultdb.ddevdb"


class Writer(DBWorker):
    """
    Class responsible for writing data to the db
    """
    def __init__(self, dbname: str, logger: logs.Logger) -> None:
        super().__init__(dbname, logger, 'a+')
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
        return super().encode_decode(str(row))

    def write_to_db(
            self,
            rows: list,
        ) -> None:
        """
        Writes data into db

        Returns written lines
        
        :params rows: List of ddevdb standardized dicts
        """
        validated_rows = []
        for row in rows:
            if self.validate_row(row):
                validated_rows.append(row)
            else:
                self.logger.log("Skipping invalid row", logs.WARNING)

        self.logger.log(f"Writing {len(validated_rows)} into db...")

        for row in validated_rows:
            encoded_row = ''.join(self.encode(row))
            self.dbfile.write(f"{encoded_row}\n")

        self.logger.log(f"Finished writing {len(validated_rows)} into db.")
        self._post_write()

        return validated_rows


class Reader(DBWorker):
    """
    Class responsible for reading data from the db
    """
    data = {}
    seek_last = 0

    def __init__(self, dbname: str, logger: logs.Logger) -> None:
        super().__init__(dbname, logger, 'rb')
        self.data = self._read_from_db()
        self.logger.log('DB Reader ready', logs.INFO)

    def decode(self, row: str) -> str:
        """
        Decode passed row
        """
        result = super().encode_decode(row)
        return ast.literal_eval(''.join(result))

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
        self.seek_last = len(self.dbfile.read())

        objects = {}
        for objid, row in enumerate(records):
            row_obj = self.decode(row.decode())
            objects[objid] = row_obj

        return objects

    def update_data(self, data: list) -> None:
        """
        Updates the reader. This allows the reader to know new data
        """
        objid = list(self.data)[-1] if self.data else 0
        for row in data:
            objid += 1
            self.data[objid] = row


    # Here begin the functions used by the lookup function
    def _infer_type(self, item: str) -> type:
        """
        Infer item object type
        """
        if item.isnumeric():
            return int(item)

        try:
            dummy = float(item)
            return float(item)
        except Exception:
            pass

        return str(item)

    def _action_list(self, targets: list) -> dict:
        """
        Return selected targets from data
        """
        result = {}
        for target in targets:
            for objid, row in self.data.items():
                if row.get(target):
                    result[objid] = row

        return result

    def _action_where(self, rowset: dict, filters: list) -> dict:
        """
        Filter given rowset
        """
        filters_dict = {}
        for f in filters:
            # Change this into another for itering through all operands
            t, v = f.split('=')
            filters_dict[t] = v

        result = {}
        for objid, row in rowset.items():
            for target, value in filters_dict.items():
                current_value = row.get(target, '')
                inferred_value = self._infer_type(value)
                if current_value and current_value == inferred_value:
                    result[objid] = row

        return result

    def lookup(self, query) -> dict:
        """
        This function should look in the data for the what
        and return it as a list/dict (probably list, to be decided)

        # How does it work
        This uses a simple pseudo query:
        #### example of simple query:
        > list: id, name; where: id=1
        """
        instructions = query.replace(" ", "").split(";")

        result = {}
        for instruction in instructions:
            action, targets = instruction.split(':')
            targets = targets.split(',')

            match [action]:
                case ['list']:
                    result = self._action_list(targets=targets)

                case ['where']:
                    result = self._action_where(result, targets)

        return result


class DataBase():
    """
    This class is the main window to interact with a ddevdb pseudo database

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

    def write(self, rows: list) -> None:
        """
        Writes data into database
        """
        rows = self.writer.write_to_db(rows)
        self.reader.update_data(data=rows)
