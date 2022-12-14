import sqlite3
import os
from pathlib import Path


class ConnectionClient:
    def __init__(self):
        self.connection = self.sqlite_con()

    @staticmethod
    def sqlite_con(db_file: str = 'cpmgs_db'):
        return sqlite3.connect(Path(os.path.abspath(os.curdir)) / '..' / db_file)
