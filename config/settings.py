import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0))


import os

DB_ENGINE = os.getenv("DB_ENGINE", "postgres")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_SSLMODE = os.getenv("POSTGRES_SSLMODE", "require")