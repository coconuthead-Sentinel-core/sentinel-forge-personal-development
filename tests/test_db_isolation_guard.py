"""Unit tests for the live-DB pollution guard (lyceum.db).

Pure logic — no GUI. Verifies the guard refuses the live database path, allows
temp paths, and that ``study_db.temp_study_db()`` isolates + restores STUDY_DB.

Run from the repo root:   python -m unittest discover -s tests
"""
import os
import tempfile
import unittest

from lyceum.db import db_location, study_db


class GuardTest(unittest.TestCase):
    def test_is_live_db_true_for_live_path(self):
        self.assertTrue(db_location.is_live_db(db_location.live_db_path()))

    def test_is_live_db_false_for_temp(self):
        self.assertFalse(db_location.is_live_db(os.path.join(tempfile.mkdtemp(), "x.db")))

    def test_is_live_db_false_for_none(self):
        self.assertFalse(db_location.is_live_db(None))

    def test_assert_raises_on_live_path(self):
        with self.assertRaises(RuntimeError):
            db_location.assert_not_live_db(db_location.live_db_path())

    def test_assert_ok_on_temp_path(self):
        db_location.assert_not_live_db(os.path.join(tempfile.mkdtemp(), "x.db"))  # no raise


class TempStudyDbTest(unittest.TestCase):
    def test_context_isolates_and_restores(self):
        before = study_db.STUDY_DB
        with study_db.temp_study_db() as tmp:
            self.assertEqual(study_db.STUDY_DB, tmp)
            self.assertNotEqual(os.path.abspath(tmp),
                                os.path.abspath(db_location.live_db_path()))
            self.assertTrue(os.path.exists(tmp))
        self.assertEqual(study_db.STUDY_DB, before)   # restored
        self.assertFalse(os.path.exists(tmp))         # cleaned up


if __name__ == "__main__":
    unittest.main()
