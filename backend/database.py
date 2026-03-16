import sqlite3
from pathlib import Path
from typing import Generator

DB_PATH = Path(__file__).parent / "data" / "campus_resources.db"


def get_db() -> Generator[sqlite3.Connection, None, None]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()
