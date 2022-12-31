from typing import List

import pandas as pd
from loguru import logger
from random_choice_data import get_random_choice_for_type
from table_data import Column, Table

from queries.create_data import create_table_q, insert_values_q
from tools.db_connection import tx_wrapper


class DataGenerator:
    def __init__(self, table: Table):
        """
        Generates random data for each of column in passed table_name.
        """
        self.table = table

    def generate_data_for_column(self, col: Column) -> List:
        return [get_random_choice_for_type(col.d_type) for _ in range(self.table.rows)]

    def generate_data_for_table(self) -> dict:
        return {
            column.column_name: self.generate_data_for_column(column)
            for column in self.table.column_info
        }

    @tx_wrapper
    def insert_data_to_table(self) -> None:
        df = pd.DataFrame(self.generate_data_for_table())
        q = insert_values_q(self.table.table_name, df)
        logger.info(f"inserted values into {self.table.table_name}")
        return q

    @tx_wrapper
    def create_table(self) -> None:
        q = create_table_q(self.table.table_name, self.table.column_info)
        logger.info(f"created {self.table.table_name}")
        return q


if __name__ == "__main__":
    t1 = Table(
        table_name="test_table_name",
        rows=5,
        column_info=(
            Column(column_name="column_1", d_type="INTEGER"),
            Column(column_name="column_2", d_type="VARCHAR(32)"),
        ),
    )
    dg = DataGenerator(t1)
