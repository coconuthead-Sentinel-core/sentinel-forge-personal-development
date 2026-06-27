"""Unit tests for the database location & backup policy (lyceum.db.db_location).

Pure filesystem/SQLite logic — no GUI. Verifies that the live DB resolves to a
local (non-synced) path, that legacy migration copies data without deleting the
original, and that snapshots are consistent, readable copies.

Run from the repo root:   python -m unittest discover -s tests
"""
import os
import sqlite3
import tempfile
import unittest

from lyceum.db import db_location


class LiveDbPathTest(unittest.TestCase):
    def test_live_path_honors_localappdata(self):
        base = tempfile.mkdtemp()
        old = os.environ.get("LOCALAPPDATA")
        os.environ["LOCALAPPDATA"] = base
        try:
            p = db_location.live_db_path()
            self.assertTrue(p.startswith(base))
            self.assertTrue(p.endswith("study.db"))
            self.assertIn(db_location.APP_NAME, p)
        finally:
            if old is None:
                os.environ.pop("LOCALAPPDATA", None)
            else:
                os.environ["LOCALAPPDATA"] = old


class MigrationTest(unittest.TestCase):
    def test_migrate_copies_without_deleting(self):
        d = tempfile.mkdtemp()
        legacy = os.path.join(d, "legacy.db")
        live = os.path.join(d, "local", "study.db")
        con = sqlite3.connect(legacy)
        con.execute("CREATE TABLE t (v TEXT)")
        con.execute("INSERT INTO t VALUES ('keep-me')")
        con.commit()
        con.close()

        self.assertTrue(db_location.migrate_legacy_if_needed(live, legacy))
        self.assertTrue(os.path.exists(live))
        self.assertTrue(os.path.exists(legacy))          # original NOT deleted
        con = sqlite3.connect(live)
        self.assertEqual(con.execute("SELECT v FROM t").fetchone()[0], "keep-me")
        con.close()

    def test_second_run_is_noop(self):
        d = tempfile.mkdtemp()
        legacy = os.path.join(d, "legacy.db")
        live = os.path.join(d, "study.db")
        sqlite3.connect(legacy).close()
        self.assertTrue(db_location.migrate_legacy_if_needed(live, legacy))
        self.assertFalse(db_location.migrate_legacy_if_needed(live, legacy))

    def test_fresh_install_no_legacy(self):
        d = tempfile.mkdtemp()
        self.assertFalse(db_location.migrate_legacy_if_needed(
            os.path.join(d, "study.db"), os.path.join(d, "absent.db")))


class SnapshotTest(unittest.TestCase):
    def test_snapshot_is_consistent_copy(self):
        d = tempfile.mkdtemp()
        live = os.path.join(d, "study.db")
        dest = os.path.join(d, "backups", "study.db")
        con = sqlite3.connect(live)
        con.execute("CREATE TABLE t (v TEXT)")
        con.execute("INSERT INTO t VALUES ('snap')")
        con.commit()
        con.close()

        out = db_location.snapshot(live, dest)
        self.assertEqual(out, dest)
        self.assertTrue(os.path.exists(dest))
        con = sqlite3.connect(dest)
        self.assertEqual(con.execute("SELECT v FROM t").fetchone()[0], "snap")
        con.close()

    def test_snapshot_missing_source_is_safe(self):
        d = tempfile.mkdtemp()
        self.assertIsNone(db_location.snapshot(os.path.join(d, "nope.db"),
                                               os.path.join(d, "out.db")))


if __name__ == "__main__":
    unittest.main()
