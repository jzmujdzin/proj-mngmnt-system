import sqlite3


class ConnectionClient:
    def __init__(self):
        self.connection = self.sqlite_con()

    @staticmethod
    def sqlite_con(db_file: str = 'cpmgs_db'):
        return sqlite3.connect(db_file)
