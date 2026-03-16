import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make backend/ importable when running pytest from the backend/ directory.
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db
from main import app

SEED_DATA = [
    # (resource_name, phone_number, email, description)
    ("Counseling and Psychological Services (CAPS)", "408-924-5678",
     "studentwellnesscenter@sjsu.edu",
     "Provides counseling services on psychological and academic issues."),
    ("Financial Aid and Scholarship Office (FASO)", "408-283-7500",
     "fao@sjsu.edu",
     "Assists students in securing federal, state, and university financial aid."),
    ("Career Center", "408-924-6031",
     "careerhelp@sjsu.edu",
     "Supports graduate students with career counseling, workshops, and planning tools."),
    ("988 Suicide & Crisis Lifeline", "988",
     "N/A",
     "24/7, free, and confidential support for people in distress and prevention resources."),
    ("National Domestic Violence Hotline", "1-800-799-7233",
     "Text START to 88788",
     "24/7 support for anyone experiencing domestic violence or seeking help."),
    ("PRIDE Center", "408-924-6976",
     "sjsupride@gmail.com",
     "Supports LGBTQ+ students and advocates for respect and safety."),
    ("SJSU Cares", "408-924-1234",
     "sjsucares@sjsu.edu",
     "Support for basic needs like food, housing, and emergency financial assistance."),
]


def _make_in_memory_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE campus_resources (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_name TEXT NOT NULL,
            phone_number  TEXT,
            email         TEXT,
            description   TEXT
        )
    """)
    con.executemany(
        "INSERT INTO campus_resources (resource_name, phone_number, email, description)"
        " VALUES (?, ?, ?, ?)",
        SEED_DATA,
    )
    con.commit()
    return con


@pytest.fixture()
def client():
    """TestClient with get_db overridden to use an in-memory SQLite database."""
    db = _make_in_memory_db()

    def override_get_db():
        try:
            yield db
        finally:
            pass  # keep alive for the duration of the test; closed below

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    db.close()
