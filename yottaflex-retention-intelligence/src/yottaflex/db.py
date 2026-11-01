from pathlib import Path
import sqlite3

def initialize_database(db_path="yottaflex.db", schema_path="database/schema.sql"):
    schema = Path(schema_path).read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        conn.execute("PRAGMA foreign_keys = ON")
    return db_path
