import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace_me")
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = os.getenv("PG_PORT", "5432")
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "")
    PG_DB = os.getenv("PG_DB", "gymdb")
