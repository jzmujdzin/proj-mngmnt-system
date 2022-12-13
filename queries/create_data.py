from typing import List
from tools.table_data import Column


def create_table_q(table_name: str, column_info: List[Column]):
    col_create = ''
    for column in column_info:
