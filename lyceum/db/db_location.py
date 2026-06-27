"""Database location & backup policy — keep the LIVE SQLite file off the
cloud-sync path, and snapshot it back into the synced folder for backup.

Rationale (verified against the academic audit, Q4): a *live* SQLite database
must not sit in a directory a background cloud daemon (OneDrive) reads/writes,
because the daemon's asynchronous reads race the database's file locks and can
produce conflicted copies or torn backups. The fix is two-fold:

  1. Open the live database from a LOCAL, non-synced directory (``%LOCALAPPDATA%``),
     where the engine has uncontested ownership of the file locks.
  2. Periodically write a *consistent, frozen* copy into the synced folder using
     SQLite's online Backup API, so the user keeps their implicit OneDrive backup
     without the live-file corruption risk.

Every function here is defensive: on any error it degrades to a safe default and
never raises, so a backup hiccup can never stop the app from starting.
"""
from __future__ import annotations

import os
import shutil
import sqlite3

APP_NAME = "SentinelForge"


def _local_base() -> str:
    """The local, non-synced app-data root (``%LOCALAPPDATA%`` on Windows)."""
    return os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")


def live_db_dir() -> str:
    return os.path.join(_local_base(), APP_NAME)


def live_db_path() -> str:
    """Where the LIVE database is opened — local disk, off the sync path."""
    return os.path.join(live_db_dir(), "study.db")


def backup_dir(study_dir: str) -> str:
    """Where frozen snapshots are written — inside the synced folder (safe:
    a closed, point-in-time copy, never the live file)."""
    return os.path.join(study_dir, "backups")


def migrate_legacy_if_needed(live_path: str, legacy_path: str) -> bool:
    """One-time, non-destructive migration: if the live DB does not yet exist
    but an older copy does (e.g. the previous OneDrive location), COPY it to the
    live location. The legacy file is left intact as a pre-migration backup.

    Returns True only when a copy was actually performed. Must run BEFORE any
    connection is opened, so the engine never creates an empty live file first.
    """
    try:
        if not live_path or not legacy_path:
            return False
        if os.path.exists(live_path):
            return False                      # already migrated, or a fresh install
        if not os.path.exists(legacy_path):
            return False                      # nothing to carry over
        os.makedirs(os.path.dirname(live_path), exist_ok=True)
        shutil.copy2(legacy_path, live_path)  # copy, never move — keep the original
        return True
    except OSError:
        return False


def snapshot(live_path: str | None = None, dest_path: str | None = None) -> str | None:
    """Write a consistent point-in-time copy of the live DB via the SQLite
    online Backup API. Returns the destination path, or None on any failure.

    Unlike a raw file copy, ``Connection.backup`` produces a transactionally
    consistent image even if the source is mid-write, so the synced snapshot is
    never torn.
    """
    try:
        live_path = live_path or live_db_path()
        if not os.path.exists(live_path):
            return None
        if dest_path is None:
            dest_path = os.path.join(live_db_dir(), "study.snapshot.db")
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        src = sqlite3.connect(live_path)
        try:
            dst = sqlite3.connect(dest_path)
            try:
                with dst:                     # commit the backup atomically
                    src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()
        return dest_path
    except (sqlite3.Error, OSError):
        return None
