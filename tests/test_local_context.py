"""Unit tests for the local-RAG retriever ranking (lyceum.local_context).

Tests the PURE ranking core (rank_snippets / score) — no files, no DB, no GUI."""
import unittest

import os
import tempfile

from lyceum.local_context import (rank_snippets, score, retrieve_context,
                                  chunk_text, retrieve_from_text)


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


class ChunkTextTest(unittest.TestCase):
    def test_short_text_one_chunk(self):
        self.assertEqual(chunk_text("hello", chunk_chars=100), ["hello"])

    def test_empty_is_no_chunks(self):
        self.assertEqual(chunk_text("   "), [])
        self.assertEqual(chunk_text(""), [])

    def test_long_text_splits_with_overlap(self):
        text = "abcdefghij" * 50          # 500 chars
        chunks = chunk_text(text, chunk_chars=200, overlap=50)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(c) <= 200 for c in chunks))
        # overlap: end of chunk 0 reappears at the start of chunk 1
        self.assertTrue(chunks[1].startswith(chunks[0][-50:]))

    def test_covers_to_end(self):
        text = "".join(str(i % 10) for i in range(1000))
        chunks = chunk_text(text, chunk_chars=300, overlap=50)
        self.assertTrue(chunks[-1].endswith(text[-10:]))


class RetrieveFromTextTest(unittest.TestCase):
    def test_pulls_relevant_passage_from_a_long_doc(self):
        doc = ("intro filler " * 200) + " the mitochondria is the powerhouse "
        doc += ("more filler " * 200)
        out = retrieve_from_text("mitochondria powerhouse", doc, chunk_chars=400)
        self.assertIn("mitochondria", out)

    def test_no_match_falls_back_to_opening(self):
        doc = "alpha beta gamma " * 100
        out = retrieve_from_text("zebra", doc, max_context=50)
        self.assertTrue(out.startswith("alpha"))
        self.assertLessEqual(len(out), 50)

    def test_empty_doc(self):
        self.assertEqual(retrieve_from_text("anything", ""), "")


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
