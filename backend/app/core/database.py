"""Small SQLite repository, with a separate connection per operation."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from uuid import uuid4


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS knowledge_bases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    description TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )"""
            )

    def check(self) -> None:
        with self.connection() as connection:
            connection.execute("SELECT 1 FROM knowledge_bases LIMIT 1").fetchone()

    def list_knowledge_bases(self) -> list[dict[str, str]]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM knowledge_bases ORDER BY created_at DESC, id"
            ).fetchall()
            return [dict(row) for row in rows]

    def create_knowledge_base(self, name: str, description: str) -> dict[str, str]:
        record = {
            "id": str(uuid4()),
            "name": name,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO knowledge_bases (id, name, description, created_at) "
                "VALUES (:id, :name, :description, :created_at)",
                record,
            )
        return record

    def get_knowledge_base(self, identifier: str) -> dict[str, str] | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM knowledge_bases WHERE id = ?", (identifier,)
            ).fetchone()
            return dict(row) if row is not None else None
