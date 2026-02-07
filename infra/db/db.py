import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "audit.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
