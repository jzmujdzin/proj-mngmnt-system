import os
import sqlite3
from pathlib import Path

import pandas as pd


def select_wrapper(q_to_execute):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect(Path(__file__).parents[1] / "cpmgs_db")
        df = pd.read_sql_query(q_to_execute(*args, **kwargs), con)
        con.close()
        return df

    return wrapper


def tx_wrapper(tx_to_execute):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect(Path(__file__).parents[1] / "cpmgs_db")
        cur = con.cursor()
        cur.execute(tx_to_execute(*args, **kwargs))
        con.commit()
        con.close()
        return

    return wrapper


if __name__ == "__main__":
    pass
