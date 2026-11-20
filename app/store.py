"""SQLite に、資料とそこから拾った項目を残す。"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Iterable, List, Tuple, Union

from .extract import Item

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    text TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    kind TEXT NOT NULL,
    date TEXT,
    text TEXT NOT NULL
);
"""


def connect(path: Union[str, Path]) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.executescript(_SCHEMA)
    return conn


def add_document(
    conn: sqlite3.Connection, name: str, raw: bytes, text: str, items: Iterable[Item]
) -> Tuple[int, bool]:
    """資料を登録する。同じ中身がすでにあれば足さない。(id, 新しく足したか) を返す。"""
    digest = hashlib.sha256(raw).hexdigest()
    row = conn.execute("SELECT id FROM documents WHERE sha256 = ?", (digest,)).fetchone()
    if row:
        return row[0], False
    with conn:
        doc_id = conn.execute(
            "INSERT INTO documents (name, sha256, text) VALUES (?, ?, ?)",
            (name, digest, text),
        ).lastrowid
        conn.executemany(
            "INSERT INTO items (document_id, kind, date, text) VALUES (?, ?, ?, ?)",
            [(doc_id, i.kind, i.date, i.text) for i in items],
        )
    return doc_id, True


def dated_items(conn: sqlite3.Connection) -> List[Tuple[int, str, str, str]]:
    """日付のある項目を (id, kind, date, text) で日付順に返す。"""
    return conn.execute(
        "SELECT id, kind, date, text FROM items WHERE date IS NOT NULL ORDER BY date, id"
    ).fetchall()
