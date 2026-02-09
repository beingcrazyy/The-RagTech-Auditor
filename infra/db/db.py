import psycopg
from pathlib import Path
from config.settings import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_SSLMODE

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def get_connection():
    return psycopg.connect(
        host=POSTGRES_HOST,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
        sslmode=POSTGRES_SSLMODE,
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        cursor.execute(f.read())

    conn.commit()
    conn.close()
