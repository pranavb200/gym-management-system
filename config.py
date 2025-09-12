import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace_me")
    ORACLE_USER = os.getenv("ORACLE_USER", "your_user")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "your_password")
    ORACLE_DSN = os.getenv("ORACLE_DSN", "yourdsn")  # e.g. "host/service"
