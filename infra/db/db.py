import sqlite3
from pathlib import Path
import psycopg


DB_PATH = Path(__file__).parent / "audit.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def get_connection():
    return psycopg.connect(
        host="regtech-postgres.postgres.database.azure.com",
        dbname="regtechdb",
        user="regtechadmin",
        password="1426327@RagTech",
        sslmode="require"
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
