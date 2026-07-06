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


class BuildIndexOverTest(unittest.TestCase):
    """The broad-folder (☁ OneDrive) walker: exclusions, relative labels,
    and cache reuse."""

    def _make_tree(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "Paperwork"))
        os.makedirs(os.path.join(d, ".git"))
        os.makedirs(os.path.join(d, "node_modules"))
        with open(os.path.join(d, "Paperwork", "lease.md"), "w",
                  encoding="utf-8") as f:
            f.write("the monthly rent is due on the first")
        with open(os.path.join(d, ".git", "notes.md"), "w",
                  encoding="utf-8") as f:
            f.write("git internals must never be indexed")
        with open(os.path.join(d, "node_modules", "readme.md"), "w",
                  encoding="utf-8") as f:
            f.write("vendored package docs must never be indexed")
        return d

    def test_excludes_repo_dirs_and_labels_relative(self):
        d = self._make_tree()
        cache = os.path.join(d, "od.json")
        idx = doc_index.build_index_over(d, cache)
        labels = [label for label, _ in idx]
        self.assertEqual(labels, [os.path.join("Paperwork", "lease.md")])
        self.assertIn("rent", idx[0][1])

    def test_cache_reused_on_second_run(self):
        d = self._make_tree()
        cache = os.path.join(d, "od.json")
        doc_index.build_index_over(d, cache)
        # Second run must hit the cache and return identical content.
        idx2 = doc_index.build_index_over(d, cache)
        self.assertEqual(len(idx2), 1)
        self.assertIn("rent", idx2[0][1])

    def test_retrieval_over_index(self):
        d = self._make_tree()
        cache = os.path.join(d, "od.json")
        idx = doc_index.build_index_over(d, cache)
        hits = retrieve_from_index("when is my rent due", idx)
        self.assertIn("rent", hits)


@unittest.skipIf(doc_index._openpyxl is None, "openpyxl not installed")
class XlsxExtractTest(unittest.TestCase):
    """Excel (.xlsx) reading for the assistant — read-only extraction."""

    def _make_xlsx(self, d):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Budget"
        ws.append(["Item", "Amount"])
        ws.append(["Rent", 900])
        ws.append(["Food", 250])
        p = os.path.join(d, "budget.xlsx")
        wb.save(p)
        return p

    def test_extracts_sheet_rows(self):
        d = tempfile.mkdtemp()
        p = self._make_xlsx(d)
        text = doc_index.extract_text(p)
        self.assertIn("Sheet: Budget", text)
        self.assertIn("Rent | 900", text)
        self.assertIn("Food | 250", text)

    def test_csv_reads_as_text(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "log.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("date,minutes\n2026-07-01,45\n")
        self.assertIn("45", doc_index.extract_text(p))

    def test_xlsx_indexed_and_retrievable(self):
        d = tempfile.mkdtemp()
        self._make_xlsx(d)
        cache = os.path.join(d, "od.json")
        idx = doc_index.build_index_over(d, cache)
        self.assertEqual(len(idx), 1)
        hits = retrieve_from_index("how much is rent", idx)
        self.assertIn("900", hits)
