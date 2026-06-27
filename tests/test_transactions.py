"""Unit tests for the atomic transaction primitive (lyceum.db.study_db).

Demonstrates ACID Atomicity directly: a multi-statement unit either lands in
full or not at all. Runs against a throwaway temp database (a standard test
fixture), so it touches neither the real study.db nor any GUI.

Run from the repo root:   python -m unittest discover -s tests
"""
import os
import tempfile
import unittest

from lyceum.db import study_db


class TransactionAtomicityTest(unittest.TestCase):
    def setUp(self):
        # Point the data layer at a fresh temp DB for the duration of the test.
        self._orig_db = study_db.STUDY_DB
        fd, self._path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        study_db.STUDY_DB = self._path
        study_db.db_exec("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")

    def tearDown(self):
        study_db.STUDY_DB = self._orig_db
        try:
            os.remove(self._path)
        except OSError:
            pass

    def _count(self) -> int:
        return study_db.db_query("SELECT COUNT(*) FROM t")[0][0]

    def test_commit_persists_all(self):
        with study_db.transaction() as con:
            con.execute("INSERT INTO t (v) VALUES ('a')")
            con.execute("INSERT INTO t (v) VALUES ('b')")
        self.assertEqual(self._count(), 2)

    def test_rollback_on_midunit_failure(self):
        # Atomicity: a failure partway through must undo the earlier write,
        # leaving zero rows — not the one that was inserted before the crash.
        with self.assertRaises(ValueError):
            with study_db.transaction() as con:
                con.execute("INSERT INTO t (v) VALUES ('first')")
                raise ValueError("simulated crash mid-unit")
        self.assertEqual(self._count(), 0)


if __name__ == "__main__":
    unittest.main()
