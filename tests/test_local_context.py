"""Unit tests for the local-RAG retriever ranking (lyceum.local_context).

Tests the PURE ranking core (rank_snippets / score) — no files, no DB, no GUI."""
import unittest

import os
import tempfile

from lyceum.local_context import rank_snippets, score, retrieve_context


class ScoreTest(unittest.TestCase):
    def test_counts_term_occurrences(self):
        self.assertEqual(score("cat cat dog", ["cat"]), 2)
        self.assertEqual(score("Cat CAT", ["cat"]), 2)        # case-insensitive
        self.assertEqual(score("nothing here", ["cat"]), 0)
        self.assertEqual(score("anything", []), 0)            # no terms


class RankSnippetsTest(unittest.TestCase):
    def setUp(self):
        self.docs = [
            ("a.md", "the cat sat on the mat"),
            ("b.md", "dogs run fast"),
            ("c.md", "cat cat cat everywhere"),
        ]

    def test_orders_by_relevance(self):
        top = rank_snippets("cat", self.docs)
        self.assertEqual([s for s, _ in top], ["c.md", "a.md"])  # b drops (0)

    def test_drops_zero_matches(self):
        top = rank_snippets("zebra", self.docs)
        self.assertEqual(top, [])

    def test_empty_query_returns_nothing(self):
        self.assertEqual(rank_snippets("", self.docs), [])

    def test_limit_is_respected(self):
        docs = [(f"{i}.md", "cat") for i in range(10)]
        self.assertEqual(len(rank_snippets("cat", docs, limit=3)), 3)

    def test_snippet_truncated(self):
        docs = [("big.md", "cat " + "x" * 5000)]
        _, snip = rank_snippets("cat", docs, max_chars=100)[0]
        self.assertEqual(len(snip), 100)

    def test_multi_term_query(self):
        top = rank_snippets("cat mat", self.docs)
        # a.md has both 'cat' and 'mat' (score 2), c.md has 'cat' x3 (score 3)
        self.assertEqual(top[0][0], "c.md")
        self.assertIn("a.md", [s for s, _ in top])


class RetrieveContextRecursionTest(unittest.TestCase):
    def test_finds_files_in_subfolders(self):
        d = tempfile.mkdtemp()
        sub = os.path.join(d, "deep", "nested")
        os.makedirs(sub)
        with open(os.path.join(sub, "note.md"), "w", encoding="utf-8") as f:
            f.write("the quokka is a small marsupial")
        ctx = retrieve_context("quokka", d)
        self.assertIn("quokka", ctx)
        self.assertIn("note.md", ctx)

    def test_indexes_txt_too(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "plain.txt"), "w", encoding="utf-8") as f:
            f.write("photosynthesis converts light to energy")
        self.assertIn("photosynthesis", retrieve_context("photosynthesis", d))

    def test_no_match_returns_empty(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "x.md"), "w", encoding="utf-8") as f:
            f.write("nothing relevant")
        self.assertEqual(retrieve_context("zebra", d), "")


if __name__ == "__main__":
    unittest.main()
