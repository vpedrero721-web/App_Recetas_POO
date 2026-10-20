from __future__ import annotations

import os

from dotenv import load_dotenv
from peewee import DatabaseProxy, MySQLDatabase


load_dotenv()

database = DatabaseProxy()
database.initialize(
    MySQLDatabase(
        os.getenv("RECETAS_DB_NAME", "recetas"),
        host=os.getenv("RECETAS_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("RECETAS_DB_PORT", "3307")),
        user=os.getenv("RECETAS_DB_USER", "root"),
        password=os.getenv("RECETAS_DB_PASSWORD", "recetas12345@"),
        charset="utf8mb4",
        connect_timeout=5,
    )
)


__all__ = ["database"]
