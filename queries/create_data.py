from typing import Tuple
from tools.table_data import Column
import pandas as pd


def create_table_q(table_name: str, column_info: Tuple[Column]) -> str:
    col_create = ''
    for column in column_info:
        col_create += f'''{column.column_name} {column.d_type} {',' if column.column_name != column_info[-1].column_name else ''}'''
    create_table_query = f'''
    CREATE TABLE {table_name} (
        {col_create}
    )
                         '''
    return create_table_query


def insert_values_q(table_name: str, df: pd.DataFrame) -> str:
    values = ''
    columns = ''
    for col in df.columns.values:
        columns += col + ','
    columns = columns[:-1]
    for row in df.iterrows():
        row_values = '('
        for i in range(len(df.columns)):
            cell = row[1][i]
            if isinstance(cell, int):
                row_values += str(cell) + ','
            else:
                row_values += f''' '{str(cell)}','''
        row_values = row_values[:-1]
        row_values += '),'
        values += row_values
    values = values[:-1]
    insert_values_query = f'''
    INSERT INTO {table_name}({columns})
    VALUES {values}
                           '''
    return insert_values_query
