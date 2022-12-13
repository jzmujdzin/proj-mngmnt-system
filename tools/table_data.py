from dataclasses import dataclass
from typing import Tuple


@dataclass
class Column:
    column_name: str
    d_type: str


@dataclass
class Table:
    table_name: str
    rows: int
    column_info: Tuple[Column]
