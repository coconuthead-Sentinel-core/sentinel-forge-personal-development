"""Tests for the cached Library indexer (lyceum.doc_index) and cross-document
retrieval (lyceum.local_context.retrieve_from_index)."""
import os
import tempfile
import unittest

from lyceum import doc_index
from lyceum.local_context import retrieve_from_index


class ExtractTextTest(unittest.TestCase):
    def test_reads_md_and_txt(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "a.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("hello world")
        self.assertEqual(doc_index.extract_text(p), "hello world")

    def test_unsupported_returns_empty(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "a.bin")
        with open(p, "w", encoding="utf-8") as f:
            f.write("x")
        self.assertEqual(doc_index.extract_text(p), "")


class BuildIndexTest(unittest.TestCase):
    def _make_library(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "sub"))
        with open(os.path.join(d, "one.md"), "w", encoding="utf-8") as f:
            f.write("the alpha document about cells")
        with open(os.path.join(d, "sub", "two.txt"), "w", encoding="utf-8") as f:
            f.write("the beta document about engines")
        return d

    def test_builds_and_caches(self):
        d = self._make_library()
        cache = os.path.join(d, "idx.json")
        idx = doc_index.build_index(d, path=cache)
        names = sorted(n for n, _ in idx)
        self.assertEqual(names, ["one.md", "two.txt"])     # recursive
        self.assertTrue(os.path.exists(cache))             # cache written
        # second run uses the cache (mtime unchanged) and returns the same set
        idx2 = doc_index.build_index(d, path=cache)
        self.assertEqual(sorted(n for n, _ in idx2), names)


class CachePathTest(unittest.TestCase):
    def test_env_override_wins(self):
        old = os.environ.get("SENTINEL_FORGE_INDEX_DIR")
        os.environ["SENTINEL_FORGE_INDEX_DIR"] = r"X:\custom"
        try:
            self.assertEqual(doc_index.cache_dir(), r"X:\custom")
            self.assertEqual(doc_index.cache_path(),
                             os.path.join(r"X:\custom", "library_index.json"))
        finally:
            if old is None:
                os.environ.pop("SENTINEL_FORGE_INDEX_DIR", None)
            else:
                os.environ["SENTINEL_FORGE_INDEX_DIR"] = old

    def test_default_is_a_real_path(self):
        self.assertTrue(doc_index.cache_path().endswith("library_index.json"))


class RetrieveFromIndexTest(unittest.TestCase):
    def setUp(self):
        self.docs = [
            ("biology.md", "the cell is the basic unit of life " * 30),
            ("cars.md", "the engine converts fuel into motion " * 30),
            ("empty.md", "nothing of interest here"),
        ]

    def test_pulls_from_the_right_book(self):
        out = retrieve_from_index("engine fuel motion", self.docs)
        self.assertIn("cars.md", out)
        self.assertIn("engine", out)

    def test_no_terms_or_no_match(self):
        self.assertEqual(retrieve_from_index("", self.docs), "")
        self.assertEqual(retrieve_from_index("zebra", self.docs), "")

    def test_doc_limit(self):
        out = retrieve_from_index("the", self.docs, doc_limit=1)
        # only one [name] header when limited to a single document
        self.assertEqual(out.count("["), 1)


if __name__ == "__main__":
    unittest.main()
