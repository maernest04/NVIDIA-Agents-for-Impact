import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/")
def list_resources(
    search: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db),
):
    if search:
        rows = db.execute(
            """
            SELECT * FROM campus_resources
            WHERE resource_name LIKE ? OR description LIKE ?
            """,
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM campus_resources").fetchall()
    return [dict(row) for row in rows]


@router.get("/{resource_id}")
def get_resource(resource_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(
        "SELECT * FROM campus_resources WHERE id = ?", (resource_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Resource not found")
    return dict(row)
