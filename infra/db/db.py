import sqlite3

DB_PATH = "infra/db/audit.db"

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=30)

def init_db():
    with open("infra/db/schema.sql") as f:
        schema = f.read()

    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
