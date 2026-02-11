from psycopg_pool import ConnectionPool
import os

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_SSLMODE = os.getenv("POSTGRES_SSLMODE", "require")

DATABASE_URL = (
    f"host={POSTGRES_HOST} "
    f"dbname={POSTGRES_DB} "
    f"user={POSTGRES_USER} "
    f"password={POSTGRES_PASSWORD} "
    f"sslmode={POSTGRES_SSLMODE}"
)

pool = ConnectionPool(conninfo=DATABASE_URL, min_size=1, max_size=5)

def get_connection():
    return pool.connection()