"""Unit tests for the Commentary store schema + CRUD queries (the data
layer behind the Glossary-style Commentary tab). Headless: temp DB, no
Tkinter. Mirrors the query shapes used by _refresh/_edit/_delete."""
import os
import tempfile
import unittest
from datetime import datetime

from lyceum.db import study_db


class CommentaryStoreTest(unittest.TestCase):
    def setUp(self):
        self._orig = study_db.STUDY_DB
        fd, self._path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        study_db.STUDY_DB = self._path
        con = study_db.connect()
        con.executescript(study_db.STUDY_SCHEMA)
        con.commit()
        con.close()

    def tearDown(self):
        study_db.STUDY_DB = self._orig
        try:
            os.remove(self._path)
        except OSError:
            pass

    def _add(self, title, body, source=""):
        now = datetime.now().isoformat(timespec="seconds")
        return study_db.db_exec(
            "INSERT INTO commentaries (title, body, source, created_at, "
            "updated_at) VALUES (?,?,?,?,?)", (title, body, source, now, now))

    def test_schema_created_and_idempotent(self):
        names = {r[0] for r in study_db.db_query(
            "SELECT name FROM sqlite_master")}
        self.assertIn("commentaries", names)
        self.assertIn("idx_commentaries_title", names)
        con = study_db.connect()
        con.executescript(study_db.STUDY_SCHEMA)   # re-run: no error
        con.commit(); con.close()

    def test_add_and_title_ordered_list(self):
        self._add("Zeta note", "z body")
        self._add("Alpha note", "a body")
        rows = study_db.db_query(
            "SELECT title FROM commentaries ORDER BY title COLLATE NOCASE")
        self.assertEqual([r[0] for r in rows], ["Alpha note", "Zeta note"])

    def test_search_title_or_body(self):
        self._add("Bushido", "the way of the warrior")
        self._add("Big-O", "growth of running time")
        def search(q):
            return study_db.db_query(
                "SELECT id FROM commentaries WHERE LOWER(title) LIKE ? "
                "OR LOWER(body) LIKE ?", (f"%{q}%", f"%{q}%"))
        self.assertEqual(len(search("warrior")), 1)   # body match
        self.assertEqual(len(search("big-o")), 1)      # title match
        self.assertEqual(len(search("nope")), 0)

    def test_edit_updates_in_place(self):
        cid = self._add("Old title", "old body")
        now = datetime.now().isoformat(timespec="seconds")
        study_db.db_exec(
            "UPDATE commentaries SET title=?, body=?, updated_at=? WHERE id=?",
            ("New title", "new body", now, cid))
        r = study_db.db_query(
            "SELECT title, body FROM commentaries WHERE id=?", (cid,))[0]
        self.assertEqual(r, ("New title", "new body"))

    def test_delete_removes_only_target(self):
        a = self._add("Keep", "k")
        b = self._add("Drop", "d")
        study_db.db_exec("DELETE FROM commentaries WHERE id=?", (b,))
        rows = study_db.db_query("SELECT id FROM commentaries")
        self.assertEqual([r[0] for r in rows], [a])

    def test_titles_need_not_be_unique(self):
        # unlike glossary term, duplicate titles are allowed
        self._add("Notes", "first")
        self._add("Notes", "second")
        self.assertEqual(
            study_db.db_query(
                "SELECT COUNT(*) FROM commentaries WHERE title='Notes'")[0][0],
            2)


if __name__ == "__main__":
    unittest.main()
