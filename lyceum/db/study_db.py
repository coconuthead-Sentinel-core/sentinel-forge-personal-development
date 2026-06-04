"""SQLite study database — paths, schema, and low-level query helpers."""
from __future__ import annotations

import os
import sqlite3
import sys

# User content (highlights, matrix, prompts, …) lives here; OneDrive backs it up.
STUDY_DIR = os.path.expanduser(r"~\OneDrive\Documents\BookReader")
STUDY_DB = os.path.join(STUDY_DIR, "study.db")

STUDY_SCHEMA = """
CREATE TABLE IF NOT EXISTS highlights (
    id INTEGER PRIMARY KEY,
    book TEXT NOT NULL,
    start_offset INTEGER NOT NULL,
    end_offset INTEGER NOT NULL,
    text TEXT,
    color TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_highlights_book ON highlights(book);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS topic_entries (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    source_book TEXT,
    source_offset INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_topic ON topic_entries(topic_id);

CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY,
    book TEXT NOT NULL,
    position INTEGER NOT NULL,
    label TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bookmarks_book ON bookmarks(book);

CREATE TABLE IF NOT EXISTS glossary (
    id INTEGER PRIMARY KEY,
    term TEXT NOT NULL COLLATE NOCASE UNIQUE,
    definition TEXT NOT NULL,
    source TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY,
    entry_date TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal(entry_date);

CREATE TABLE IF NOT EXISTS eisenhower (
    quadrant TEXT PRIMARY KEY,
    body TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS study_notes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    body TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS day_blocks (
    id INTEGER PRIMARY KEY,
    block_date TEXT NOT NULL,
    slot_order INTEGER NOT NULL,
    duration_min INTEGER NOT NULL,
    title TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    done INTEGER NOT NULL DEFAULT 0,
    is_current INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_blocks_date ON day_blocks(block_date);

CREATE TABLE IF NOT EXISTS workflow_folders (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    date_label TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL DEFAULT 'green',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(name COLLATE NOCASE)
);

CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL DEFAULT '',
    overall_grade TEXT NOT NULL DEFAULT '',
    mentors_note TEXT NOT NULL DEFAULT '',
    findings_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY,
    prompt TEXT NOT NULL DEFAULT '',
    purpose TEXT NOT NULL DEFAULT '',
    refs TEXT NOT NULL DEFAULT '',
    iterations TEXT NOT NULL DEFAULT '',
    ai_tools TEXT NOT NULL DEFAULT '',
    input_type TEXT NOT NULL DEFAULT '',
    output_type TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def init_study_db() -> None:
    """Create the study database and its tables if they don't exist."""
    try:
        os.makedirs(STUDY_DIR, exist_ok=True)
    except OSError as e:
        print(f"[lyceum.db] Could not create {STUDY_DIR}: {e}", file=sys.stderr)
        return
    try:
        con = connect()
        con.executescript(STUDY_SCHEMA)
        con.commit()
        con.close()
    except sqlite3.Error as e:
        print(f"[lyceum.db] DB init error: {e}", file=sys.stderr)


def connect() -> sqlite3.Connection:
    """Return a fresh connection. Each caller closes it after use."""
    con = sqlite3.connect(STUDY_DB)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def db_query(sql: str, params: tuple = ()) -> list[tuple]:
    con = connect()
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def db_exec(sql: str, params: tuple = ()) -> int:
    """Execute a write; return the last inserted rowid (or 0)."""
    con = connect()
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid or 0
    finally:
        con.close()