"""Headless tests for the Prompt Library archive kernel + schema migration.

Owner QA find (2026-07-20): red Delete hard-deleted Prompt Library
entries. The repair archives instead — these tests pin the kernel
(Markdown rendering, safe filenames) and the additive archived_at
migration, on a temp DB only (never the live study.db).
"""

import sqlite3
import unittest

from lyceum import prompt_archive
from lyceum.db import study_db


class TestSafeSlug(unittest.TestCase):
    def test_ordinary_title(self):
        self.assertEqual(prompt_archive.safe_slug("Motivation and life"),
                         "Motivation-and-life")

    def test_windows_unsafe_characters_removed(self):
        slug = prompt_archive.safe_slug('a<b>c:d"e/f\\g|h?i*j')
        for ch in '<>:"/\\|?*':
            self.assertNotIn(ch, slug)

    def test_empty_title_falls_back(self):
        self.assertEqual(prompt_archive.safe_slug(""), "untitled")
        self.assertEqual(prompt_archive.safe_slug("///"), "untitled")

    def test_length_capped(self):
        self.assertLessEqual(len(prompt_archive.safe_slug("x" * 200)), 40)


class TestArchiveFilename(unittest.TestCase):
    def test_contains_id_slug_stamp(self):
        name = prompt_archive.archive_filename(
            7, "Job search notes", "2026-07-20T14:03:11")
        self.assertTrue(name.startswith("PROMPTLIB-0007_"))
        self.assertIn("Job-search-notes", name)
        self.assertTrue(name.endswith(".md"))
        self.assertNotIn(":", name)          # Windows-safe

    def test_identical_titles_stay_unique_by_id(self):
        a = prompt_archive.archive_filename(1, "Same", "2026-07-20T09:00:00")
        b = prompt_archive.archive_filename(2, "Same", "2026-07-20T09:00:00")
        self.assertNotEqual(a, b)


class TestEntryToMarkdown(unittest.TestCase):
    ENTRY = {
        "id": 12,
        "title": "Top-down review",
        "prompt": "Can we review the repo as point of truth?",
        "response": "Yes — three references confirmed.",
        "source": "chat",
        "created_at": "2026-07-20T13:00:00",
        "archived_at": "2026-07-20T14:00:00",
    }

    def test_front_matter_and_body_present(self):
        md = prompt_archive.entry_to_markdown(self.ENTRY)
        self.assertTrue(md.startswith("---"))
        for needle in ("doc_id:      PROMPTLIB-0012",
                       "archived_at: 2026-07-20T14:00:00",
                       "## Prompt (the owner's message)",
                       "Can we review the repo as point of truth?",
                       "## Response (the reply)",
                       "Yes — three references confirmed."):
            self.assertIn(needle, md)

    def test_word_count_counts_prompt_plus_response(self):
        md = prompt_archive.entry_to_markdown(
            {"id": 1, "title": "t", "prompt": "one two three",
             "response": "four five"})
        self.assertIn("word_count:  5", md)

    def test_blank_fields_never_refuse(self):
        md = prompt_archive.entry_to_markdown({"id": 3})
        self.assertIn("(untitled)", md)
        self.assertIn("word_count:  0", md)


class TestArchivedAtMigration(unittest.TestCase):
    def test_fresh_schema_has_archived_at(self):
        with study_db.temp_study_db() as tmp:
            con = sqlite3.connect(tmp)
            con.executescript(study_db.STUDY_SCHEMA)
            cols = {r[1] for r in con.execute(
                "PRAGMA table_info(prompt_library)").fetchall()}
            con.close()
            self.assertIn("archived_at", cols)

    def test_old_table_gains_archived_at_additively(self):
        with study_db.temp_study_db() as tmp:
            con = sqlite3.connect(tmp)
            # v0.9-era table without the column, with one live row.
            con.execute(
                "CREATE TABLE prompt_library ("
                " id INTEGER PRIMARY KEY, title TEXT NOT NULL DEFAULT '',"
                " prompt TEXT NOT NULL DEFAULT '',"
                " response TEXT NOT NULL DEFAULT '',"
                " source TEXT NOT NULL DEFAULT '',"
                " created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
            con.execute(
                "INSERT INTO prompt_library"
                " (title, prompt, response, source, created_at, updated_at)"
                " VALUES ('keep me','p','r','','2026-01-01','2026-01-01')")
            con.commit()
            # The same additive step init_study_db runs.
            have = {r[1] for r in con.execute(
                "PRAGMA table_info(prompt_library)").fetchall()}
            if "archived_at" not in have:
                con.execute("ALTER TABLE prompt_library "
                            "ADD COLUMN archived_at TEXT")
            rows = con.execute(
                "SELECT title, archived_at FROM prompt_library").fetchall()
            con.close()
            self.assertEqual(rows, [("keep me", None)])   # data survives, active

    def test_archive_is_an_update_not_a_delete(self):
        with study_db.temp_study_db() as tmp:
            con = sqlite3.connect(tmp)
            con.executescript(study_db.STUDY_SCHEMA)
            con.execute(
                "INSERT INTO prompt_library"
                " (title, prompt, response, source, created_at, updated_at)"
                " VALUES ('old','p','r','','2026-01-01','2026-01-01')")
            con.execute(
                "UPDATE prompt_library SET archived_at='2026-07-20T14:00:00'"
                " WHERE title='old'")
            active = con.execute(
                "SELECT COUNT(*) FROM prompt_library"
                " WHERE archived_at IS NULL").fetchone()[0]
            total = con.execute(
                "SELECT COUNT(*) FROM prompt_library").fetchone()[0]
            con.close()
            self.assertEqual(active, 0)   # left the active list…
            self.assertEqual(total, 1)    # …but the row is still there


if __name__ == "__main__":
    unittest.main()
