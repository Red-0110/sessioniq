import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Prefer DATABASE_URL (Postgres) when set; otherwise use local SQLite
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local SQLite file in instance/ folder
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(BASE_DIR / "instance" / "sessioniq.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False