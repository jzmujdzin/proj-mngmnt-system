from dataclasses import dataclass
from typing import Tuple


@dataclass
class Column:
    column_name: str
    d_type: str
    data_ranges: Tuple[int, int]
