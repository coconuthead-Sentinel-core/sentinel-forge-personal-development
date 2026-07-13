"""Unit tests for the V2MOM if-then column (Sprint D).

Pure DB logic — no GUI. Verifies the additive migration adds `if_then` to an
OLD-schema table without touching existing rows, the fresh schema carries it,
and a row round-trips. The line is optional by design (implementation
intentions are encouraged, never required), so '' must be a valid value.

Run from the repo root:   python -m unittest discover -s tests
"""
import os
import sqlite3
import tempfile
import unittest

from lyceum.db import study_db


class MigrationTest(unittest.TestCase):
    def test_old_schema_gains_if_then_without_data_loss(self):
        with study_db.temp_study_db() as tmp:
            con = sqlite3.connect(tmp)
            # Build the OLD v2mom table (no if_then) with one row.
            con.execute("""CREATE TABLE v2mom_goals (
                id INTEGER PRIMARY KEY,
                vision TEXT NOT NULL DEFAULT '',
                values_why TEXT NOT NULL DEFAULT '',
                methods TEXT NOT NULL DEFAULT '',
                obstacles TEXT NOT NULL DEFAULT '',
                measurement TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL)""")
            con.execute("INSERT INTO v2mom_goals (vision, values_why, "
                        "obstacles, created_at, updated_at) "
                        "VALUES ('V','W','O','t','t')")
            con.commit(); con.close()

            study_db.init_study_db()

            con = sqlite3.connect(tmp)
            cols = {r[1] for r in con.execute(
                "PRAGMA table_info(v2mom_goals)").fetchall()}
            self.assertIn("if_then", cols)
            row = con.execute("SELECT vision, values_why, if_then "
                              "FROM v2mom_goals").fetchone()
            self.assertEqual(row, ("V", "W", ""))   # data intact; default ''
            con.close()

    def test_fresh_schema_has_if_then_and_roundtrips(self):
        with study_db.temp_study_db() as tmp:
            study_db.init_study_db()
            con = sqlite3.connect(tmp)
            con.execute("INSERT INTO v2mom_goals (vision, values_why, "
                        "obstacles, if_then, created_at, updated_at) "
                        "VALUES ('V','W','O','If it rains, then I run "
                        "indoors','t','t')")
            con.commit()
            got = con.execute("SELECT if_then FROM v2mom_goals").fetchone()[0]
            self.assertEqual(got, "If it rains, then I run indoors")
            con.close()

    def test_if_then_is_optional(self):
        with study_db.temp_study_db() as tmp:
            study_db.init_study_db()
            con = sqlite3.connect(tmp)
            con.execute("INSERT INTO v2mom_goals (vision, values_why, "
                        "obstacles, created_at, updated_at) "
                        "VALUES ('V','W','O','t','t')")   # no if_then given
            con.commit()
            got = con.execute("SELECT if_then FROM v2mom_goals").fetchone()[0]
            self.assertEqual(got, "")                      # defaults, no error
            con.close()


if __name__ == "__main__":
    unittest.main()
