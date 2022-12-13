import sqlite3
from typing import List

import pandas as pd
from loguru import logger
from random_choice_data import get_random_choice_for_type
from table_data import Column, Table

from queries.create_data import create_table_q, insert_values_q


class DataGenerator:
    def __init__(self, table: Table, con: sqlite3.Connection):
        """
        Generates random data for each of column in passed table_name, with provided data_ranges.
        """
        self.table = table
        self.con = con
        self.cur = self.con.cursor()

    def generate_data_for_column(self, col: Column) -> List:
        return [
            get_random_choice_for_type(col.d_type) for row in range(self.table.rows)
        ]

    def generate_data_for_table(self) -> List[List]:
        return [
            self.generate_data_for_column(column) for column in self.table.column_info
        ]

    def insert_data_to_table(self) -> None:
        df = pd.DataFrame(self.generate_data_for_table())
        q = insert_values_q(self.table.table_name, df)
        self.cur.execute(q)
        logger.info(f"inserted values into {self.table.table_name}")

    def create_table(self) -> None:
        q = create_table_q(self.table.table_name, self.table.column_info)
        self.cur.execute(q)
        logger.info(f"created {self.table.table_name}")
