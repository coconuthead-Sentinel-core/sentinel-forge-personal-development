"""Unit tests for lyceum/harvest.py — the Knowledge Harvester core.

Every junk-rejection test reproduces a REAL bad hit from the practice
corpus (two captured Office textbooks); the filters exist because these
exact shapes appeared.
"""
import unittest

from lyceum.harvest import harvest


GOOD = ("Journal entries are the primary document used by accountants "
        "to make adjustments at the end of the month or year. ")


class HarvestTest(unittest.TestCase):
    def test_extracts_clean_definition(self):
        cards = harvest(GOOD)
        self.assertEqual(len(cards), 1)
        term, defn, score = cards[0]
        self.assertEqual(term, "Journal entries")
        self.assertTrue(defn.startswith("The primary document"))
        self.assertGreater(score, 0)

    def test_rejects_author_bios(self):
        text = ("Joan is the author of more than two dozen books about "
                "Windows and Microsoft Office for enterprise users. ")
        self.assertEqual(harvest(text), [])

    def test_rejects_sentence_fragments(self):
        text = ("Whether you are a novice document writer or an expert, "
                "the tools help daily. "
                "Where is the data for your table field placed today. ")
        self.assertEqual(harvest(text), [])

    def test_rejects_marketing_hype(self):
        text = ("Accounting 2007 is a powerful tool in growing and "
                "operating a successful business venture. ")
        self.assertEqual(harvest(text), [])

    def test_rejects_generic_terms(self):
        text = ("The result is a net book value when the asset and "
                "contra-asset accounts are combined together. ")
        self.assertEqual(harvest(text), [])

    def test_comma_splice_cut_to_first_clause(self):
        text = ("Vendors are the companies and individuals from whom you "
                "purchase goods and services, the publication is a "
                "half-sheet side-fold card with extras. ")
        cards = harvest(text)
        self.assertEqual(len(cards), 1)
        self.assertNotIn("publication", cards[0][1])
        self.assertTrue(cards[0][1].endswith("services."))

    def test_dedupe_keeps_best_score(self):
        text = (GOOD + GOOD +
                "journal entries are the entries you should review. ")
        cards = harvest(text)
        terms = [t.casefold() for t, _d, _s in cards]
        self.assertEqual(terms.count("journal entries"), 1)

    def test_max_terms_cap_and_ordering(self):
        text = "".join(
            f"Widget{i} is a collection of items sold as a group here. "
            for i in range(30))
        cards = harvest(text, max_terms=10)
        self.assertEqual(len(cards), 10)
        scores = [s for _t, _d, s in cards]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_empty_and_plain_text(self):
        self.assertEqual(harvest(""), [])
        self.assertEqual(harvest("No definitions live here at all."), [])

    def test_deterministic(self):
        text = GOOD + ("A kit is a collection of items sold together as "
                       "one convenient group for customers. ")
        self.assertEqual(harvest(text), harvest(text))


if __name__ == "__main__":
    unittest.main()
