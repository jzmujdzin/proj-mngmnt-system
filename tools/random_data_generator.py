import pandas as pd
import random
import sqlite3
from typing import List
from table_data import Column


class DataGenerator:

    def __init__(self, table_name: str, column_info: List[Column], con: sqlite3.Connection):
        """
        Generates random data for each of column in passed table_name, with provided data_ranges.
        """
        self.table_name = table_name
        self.column_info = column_info
        self.con = con
        self.cur = self.con.cursor()

    def generate_data_for_column(self, column_name: str):
        pass

    def create_table(self):
        pass

