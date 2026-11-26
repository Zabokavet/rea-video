"""The audio library: narration records in SQLite, audio files on disk."""
from __future__ import annotations

import shutil
import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS narrations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    provider TEXT NOT NULL,
    voice TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL,          -- queued | generating | ready | failed
    error TEXT,
    chunks_total INTEGER NOT NULL DEFAULT 0,
    chunks_done INTEGER NOT NULL DEFAULT 0,
    has_mp3 INTEGER NOT NULL DEFAULT 0,
    has_wav INTEGER NOT NULL DEFAULT 0,
    sample_rate INTEGER,
    duration REAL,
    created_at TEXT NOT NULL,
    finished_at TEXT
);
"""

_PUBLIC = ("id", "title", "provider", "voice", "model", "status", "error", "chunks_total",
           "chunks_done", "has_mp3", "has_wav", "sample_rate", "duration", "created_at", "finished_at")


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class Library:
    def __init__(self, data_dir: Path):
        self.root = Path(data_dir)
        self.audio_root = self.root / "audio"
        self.audio_root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(self.root / "library.sqlite3", check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_SCHEMA)
        # Jobs interrupted by a restart can't resume mid-stream; let the user retry them.
        self._db.execute("UPDATE narrations SET status='failed', error='Interrupted by a server restart. "
                         "Use Retry to generate it again.' WHERE status IN ('queued','generating')")
        self._db.commit()

    def dir_for(self, nid: str) -> Path:
        return self.audio_root / nid

    def file_for(self, nid: str, ext: str) -> Path:
        return self.dir_for(nid) / f"narration.{ext}"

    def create(self, title: str, text: str, provider: str, voice: str, model: str) -> dict:
        nid = uuid.uuid4().hex
        with self._lock:
            self._db.execute(
                "INSERT INTO narrations (id,title,text,provider,voice,model,status,created_at) "
                "VALUES (?,?,?,?,?,?,'queued',?)", (nid, title, text, provider, voice, model, now()))
            self._db.commit()
        return self.get(nid)

    def update(self, nid: str, **fields) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k}=?" for k in fields)
        with self._lock:
            self._db.execute(f"UPDATE narrations SET {cols} WHERE id=?", (*fields.values(), nid))
            self._db.commit()

    def get(self, nid: str, with_text: bool = False) -> dict | None:
        with self._lock:
            row = self._db.execute("SELECT * FROM narrations WHERE id=?", (nid,)).fetchone()
        return self._public(row, with_text) if row else None

    def list(self, query: str = "") -> list[dict]:
        sql, args = "SELECT * FROM narrations", ()
        if query:
            sql += " WHERE title LIKE ? OR text LIKE ?"
            args = (f"%{query}%", f"%{query}%")
        sql += " ORDER BY created_at DESC, rowid DESC"
        with self._lock:
            rows = self._db.execute(sql, args).fetchall()
        return [self._public(r) for r in rows]

    def delete(self, nid: str) -> bool:
        with self._lock:
            cur = self._db.execute("DELETE FROM narrations WHERE id=?", (nid,))
            self._db.commit()
        shutil.rmtree(self.dir_for(nid), ignore_errors=True)
        return cur.rowcount > 0

    @staticmethod
    def _public(row: sqlite3.Row, with_text: bool = False) -> dict:
        d = {k: row[k] for k in _PUBLIC}
        d["has_mp3"], d["has_wav"] = bool(d["has_mp3"]), bool(d["has_wav"])
        d["characters"] = len(row["text"])
        d["excerpt"] = row["text"][:160]
        if with_text:
            d["text"] = row["text"]
        return d
