from typing import List
from tools.table_data import Column


def create_table_q(table_name: str, column_info: List[Column]) -> str:
    col_create = ''
    for column in column_info:
        col_create += f'''{column.column_name} {column.d_type} {',' if column.column_name != column_info[-1].column_name else ''}'''
    create_table_query = f'''
    CREATE TABLE {table_name} (
        {col_create}
    )
                         '''
    return create_table_query
