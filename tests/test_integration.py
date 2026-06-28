"""Integration tests — exercise multiple modules together (not just isolated
units): the real DB schema + data layer + domain logic, the RAG index→retrieve
pipeline, the dictation pipeline, and the read-aloud pipeline. All headless."""
import os
import tempfile
import unittest
from datetime import date

from lyceum.db import study_db
from lyceum import goals, doc_index, local_context


class DatabaseIntegrationTest(unittest.TestCase):
    """Real schema on a throwaway DB → CRUD → domain logic + FK cascade."""

    def setUp(self):
        self._orig = study_db.STUDY_DB
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        study_db.STUDY_DB = self.path
        con = study_db.connect()
        con.executescript(study_db.STUDY_SCHEMA)   # the real production schema
        con.commit()
        con.close()

    def tearDown(self):
        study_db.STUDY_DB = self._orig
        try:
            os.remove(self.path)
        except OSError:
            pass

    def test_goals_roundtrip_through_summarize(self):
        study_db.db_exec(
            "INSERT INTO goals (title,progress,status,target_date,created_at,updated_at)"
            " VALUES (?,?,?,?,?,?)",
            ("Finish C# course", 100, "active", "", "2026-01-01", "2026-01-01"))
        study_db.db_exec(
            "INSERT INTO goals (title,progress,status,target_date,created_at,updated_at)"
            " VALUES (?,?,?,?,?,?)",
            ("Run 5k", 5, "active", "2026-12-31", "2026-01-01", "2026-01-01"))
        rows = study_db.db_query(
            "SELECT created_at,target_date,progress,status FROM goals ORDER BY id")
        _per, (n_bad, n_ok, n_done) = goals.summarize(rows, today=date(2026, 6, 28))
        self.assertEqual(n_done, 1)     # the 100% goal
        self.assertEqual(n_bad, 1)      # 5% with half the year gone -> behind

    def test_fk_cascade_inside_transaction(self):
        tid = study_db.db_exec(
            "INSERT INTO topics (title,created_at) VALUES (?,?)", ("DB", "2026-01-01"))
        study_db.db_exec(
            "INSERT INTO topic_entries (topic_id,text,created_at) VALUES (?,?,?)",
            (tid, "ACID means atomic", "2026-01-01"))
        with study_db.transaction() as con:
            con.execute("DELETE FROM topics WHERE id=?", (tid,))
        # ON DELETE CASCADE (with PRAGMA foreign_keys=ON) removed the child rows
        self.assertEqual(
            study_db.db_query("SELECT COUNT(*) FROM topic_entries")[0][0], 0)


class RagPipelineIntegrationTest(unittest.TestCase):
    """doc_index.build_index → local_context.retrieve_from_index."""

    def test_index_then_retrieve(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "sub"))
        with open(os.path.join(d, "a.md"), "w", encoding="utf-8") as f:
            f.write("photosynthesis converts sunlight into chemical energy")
        with open(os.path.join(d, "sub", "b.txt"), "w", encoding="utf-8") as f:
            f.write("the mitochondria is the powerhouse of the cell")
        idx = doc_index.build_index(d, path=os.path.join(d, "idx.json"))
        out = local_context.retrieve_from_index("mitochondria powerhouse", idx)
        self.assertIn("mitochondria", out)
        self.assertIn("b.txt", out)


class DictationPipelineIntegrationTest(unittest.TestCase):
    """The live _append_dictation order: spoken commands then collision dedup."""

    def test_commands_then_guard(self):
        from lyceum.dictation_commands import apply_dictation_commands
        from lyceum.dictation_guard import dedup_punctuation
        # user said "period" twice (or Whisper + user collided)
        out = dedup_punctuation(apply_dictation_commands("meeting at noon period period"))
        self.assertEqual(out, "meeting at noon.")


class ReadPipelineIntegrationTest(unittest.TestCase):
    """The read-aloud front end: text normalization then sentence chunking."""

    def test_normalize_then_chunk(self):
        from lyceum.text_norm import normalize_for_speech
        from lyceum.voice_pipeline import iter_sentences
        spoken = normalize_for_speech("In 1999 it cost $5. We kept 50%.")
        joined = " ".join(iter_sentences([spoken]))
        self.assertIn("nineteen ninety-nine", joined)
        self.assertIn("five dollars", joined)
        self.assertIn("fifty percent", joined)


if __name__ == "__main__":
    unittest.main()
