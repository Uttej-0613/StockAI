import json
import sqlite3
from pathlib import Path
from typing import Any
from backend.config import get_settings

def connect() -> sqlite3.Connection:
    settings = get_settings()
    settings.ensure_data_dir()
    db = sqlite3.connect(Path(settings.database_path).expanduser(), timeout=20)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def initialize() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            sha256 TEXT NOT NULL UNIQUE,
            chunks INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT,
            UNIQUE(document_id, chunk_index)
        );
        CREATE TABLE IF NOT EXISTS watchlist (
            symbol TEXT PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)

def save_document(filename: str, digest: str, chunks: list[dict[str, Any]]) -> int:
    with connect() as db:
        existing = db.execute("SELECT id FROM documents WHERE sha256=?", (digest,)).fetchone()
        if existing:
            return int(existing["id"])
        cur = db.execute("INSERT INTO documents(filename,sha256,chunks) VALUES(?,?,?)", (filename, digest, len(chunks)))
        doc_id = int(cur.lastrowid)
        db.executemany(
            "INSERT INTO chunks(document_id,chunk_index,content,embedding) VALUES(?,?,?,?)",
            [(doc_id, i, c["content"], json.dumps(c["embedding"]) if c.get("embedding") else None) for i,c in enumerate(chunks)]
        )
        return doc_id

def list_documents() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT id,filename,chunks,created_at FROM documents ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_chunks() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("""SELECT c.id,c.content,c.embedding,d.filename,d.id AS document_id,c.chunk_index
                             FROM chunks c JOIN documents d ON d.id=c.document_id""").fetchall()
        return [dict(r) for r in rows]

def add_watchlist(symbol: str) -> None:
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO watchlist(symbol) VALUES(?)", (symbol.upper(),))

def get_watchlist() -> list[str]:
    with connect() as db:
        return [r["symbol"] for r in db.execute("SELECT symbol FROM watchlist ORDER BY symbol")]

def remove_watchlist(symbol: str) -> None:
    with connect() as db:
        db.execute("DELETE FROM watchlist WHERE symbol=?", (symbol.upper(),))
