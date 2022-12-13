from typing import Tuple
from tools.table_data import Column
import pandas as pd


def create_table_q(table_name: str, column_info: Tuple[Column]) -> str:
    """
    Creates query for table creation

    Using provided params, table_name and column_info, function iterates over columns in the column_info tuple,
    appends needed information to the query about column name and column data type.

    table_name: str -- name of the table
    column_info: Tuple[Column] -- tuple of Column dataclasses with column information (column_name and data type)

    Returns:
    String in the form of SQL query that when executed by cursor, creates the table
    """
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
    """
    Inserts values from dataframe into table

    Iterates over every row in the dataframe, checks its type and appends it to the query

    table_name: str -- name of the table
    df -- dataframe with data to insert to table

    Returns:
    String in the form of SQL query that when executed by cursor, inserts values into the table
    """
    values = ''
    columns = ''
    # iterates over columns and appends them to the columns string
    # df.columns.values returns i.e. array(['nums', 'letters'], dtype=object)
    # this converts it to (nums, letters) for applicable to be executed inside the query
    for col in df.columns.values:
        columns += col + ','
    # strips the last, obsolete comma
    columns = columns[:-1]
    # iterates over all rows
    for row in df.iterrows():
        row_values = '('
        # iterates over every cell
        for i in range(len(df.columns)):
            cell = row[1][i]
            # check if cell is the int type
            # this is needed because the string types should be input into query with apostrophes
            # i.e. we have two values, 'a' and 1
            # for a, it adds 'a' to query, for 1 it adds 1 to query
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
