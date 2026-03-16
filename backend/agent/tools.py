import sqlite3

from langchain_core.tools import tool

from database import DB_PATH


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _rows_to_text(rows) -> str:
    if not rows:
        return "No matching resources found."
    parts = []
    for r in rows:
        lines = [f"**{r['resource_name']}**", f"Phone: {r['phone_number']}"]
        if r["email"] and r["email"] != "N/A":
            lines.append(f"Email/Text: {r['email']}")
        lines.append(r["description"])
        parts.append("\n".join(lines))
    return "\n\n---\n\n".join(parts)


@tool
def search_resources(query: str) -> str:
    """Search SJSU campus resources and national crisis hotlines by keyword.

    Use this to find resources matching a topic such as 'mental health',
    'housing', 'food', 'financial aid', 'crisis', 'LGBTQ', 'domestic violence',
    'veterans', etc. Searches both resource names and descriptions.
    Returns matching resources with phone numbers and descriptions.
    """
    con = _db()
    rows = con.execute(
        """
        SELECT resource_name, phone_number, email, description
        FROM campus_resources
        WHERE resource_name LIKE ? OR description LIKE ?
        """,
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    con.close()
    return _rows_to_text(rows)


@tool
def get_resource_by_name(name: str) -> str:
    """Retrieve a specific campus resource or hotline by its exact or partial name.

    Use this when you already know the name of the resource you want, such as
    'CAPS', 'SJSU Cares', '988', 'PRIDE Center', etc.
    Returns the resource's phone number, email, and description.
    """
    con = _db()
    row = con.execute(
        "SELECT resource_name, phone_number, email, description FROM campus_resources WHERE resource_name LIKE ?",
        (f"%{name}%",),
    ).fetchone()
    con.close()
    if not row:
        return f"No resource found matching '{name}'."
    return _rows_to_text([row])
