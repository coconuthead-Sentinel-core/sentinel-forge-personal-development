"""Unit tests for pure Idea-Warehouse logic (lyceum.ideas), extracted from the
CC-60 open_idea_warehouse builder."""
import unittest

from lyceum import ideas

# priority rank as built in the GUI from self._ABCDE
PRANK = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}


def row(id_, pri="", big=0, sched="", status="open"):
    return (id_, f"task {id_}", pri, big, sched, status)


class OrderTasksTest(unittest.TestCase):
    def test_open_before_scheduled(self):
        rows = [row(1, status="scheduled"), row(2, status="open")]
        self.assertEqual([r[0] for r in ideas.order_tasks(rows, PRANK)], [2, 1])

    def test_big_three_first(self):
        rows = [row(1, big=0), row(2, big=1)]
        self.assertEqual([r[0] for r in ideas.order_tasks(rows, PRANK)], [2, 1])

    def test_priority_then_id(self):
        rows = [row(3, "C"), row(1, "A"), row(2, "A"), row(4, "")]
        # A's first (by id), then C, then untagged last
        self.assertEqual([r[0] for r in ideas.order_tasks(rows, PRANK)],
                         [1, 2, 3, 4])

    def test_full_precedence(self):
        rows = [
            row(1, "A", status="scheduled"),   # scheduled -> last group
            row(2, "C", big=1),                # open, big-three
            row(3, "A"),                       # open, A
        ]
        self.assertEqual([r[0] for r in ideas.order_tasks(rows, PRANK)], [2, 3, 1])


class BannerCountsTest(unittest.TestCase):
    def test_counts(self):
        rows = [
            row(1, "A"),                       # open A  -> open_a
            row(2, "A", status="scheduled"),   # not open
            row(3, "B", big=1),                # open big -> big_open
            row(4, "A", big=1),                # open A AND big -> both
        ]
        open_a, big_open = ideas.banner_counts(rows)
        self.assertEqual((open_a, big_open), (2, 2))


if __name__ == "__main__":
    unittest.main()
