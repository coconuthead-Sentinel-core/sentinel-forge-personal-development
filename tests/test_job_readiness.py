"""Unit tests for the pure job-readiness audit kernel (lyceum.job_readiness).

Covers scoring, band classification, next-move ranking (weakest-first with
foundational tie-break), check-in comparison, and tolerant round-tripping of
stored scores. The DB round-trip runs against ``temp_study_db()`` — never the
live database.

Run from the repo root:   python -m unittest discover -s tests
"""
import unittest

from lyceum import job_readiness as jr
from lyceum.db import study_db


def scores(**kw):
    """All-zero score dict, overridden by keyword."""
    s = {k: 0 for k in jr.PILLAR_KEYS}
    s.update(kw)
    return s


class RubricShapeTest(unittest.TestCase):
    def test_every_pillar_has_full_rubric_and_steps(self):
        for key in jr.PILLAR_KEYS:
            self.assertEqual(len(jr.RUBRIC[key]), jr.MAX_SCORE + 1, key)
            self.assertEqual(len(jr.NEXT_STEP[key]), jr.MAX_SCORE, key)


class ClampTest(unittest.TestCase):
    def test_clamps_and_tolerates_garbage(self):
        self.assertEqual(jr.clamp(-3), 0)
        self.assertEqual(jr.clamp(99), 4)
        self.assertEqual(jr.clamp("2"), 2)
        self.assertEqual(jr.clamp(None), 0)
        self.assertEqual(jr.clamp("banana"), 0)


class ReadinessTest(unittest.TestCase):
    def test_all_zero_is_cold_start(self):
        pct, band, badge = jr.readiness(scores())
        self.assertEqual((pct, band), (0, "cold_start"))
        self.assertIn("COLD START", badge)

    def test_all_max_is_offer_ready(self):
        pct, band, _ = jr.readiness({k: 4 for k in jr.PILLAR_KEYS})
        self.assertEqual((pct, band), (100, "offer_ready"))

    def test_band_floors(self):
        # 6 pillars x 4 = 24 points; 12 points = 50% -> warming_up.
        pct, band, _ = jr.readiness({k: 2 for k in jr.PILLAR_KEYS})
        self.assertEqual((pct, band), (50, "warming_up"))
        # 18 points = 75% -> in_the_hunt; 20 points = 83% -> interview_ready.
        self.assertEqual(jr.readiness({k: 3 for k in jr.PILLAR_KEYS})[1],
                         "in_the_hunt")
        pct, band, _ = jr.readiness(scores(
            story=4, proof=4, skills=4, people=4, pipeline=4))
        self.assertEqual((pct, band), (83, "interview_ready"))

    def test_missing_pillars_count_as_zero(self):
        self.assertEqual(jr.readiness({})[0], 0)
        self.assertEqual(jr.readiness({"story": 4})[0], round(100 * 4 / 24))


class NextMovesTest(unittest.TestCase):
    def test_weakest_pillar_first(self):
        moves = jr.next_moves(scores(story=4, proof=3, skills=1, people=2,
                                     pipeline=2, interview=3))
        self.assertEqual(moves[0][0], "skills")
        self.assertEqual(moves[0][3], jr.NEXT_STEP["skills"][1])

    def test_foundational_order_breaks_ties(self):
        # Everything tied at 0 -> story (most foundational) leads.
        moves = jr.next_moves(scores())
        self.assertEqual([m[0] for m in moves], ["story", "proof", "skills"])

    def test_maxed_pillars_are_excluded(self):
        moves = jr.next_moves({k: 4 for k in jr.PILLAR_KEYS}, k=6)
        self.assertEqual(moves, [])

    def test_k_limits_results(self):
        self.assertEqual(len(jr.next_moves(scores(), k=2)), 2)


class CompareTest(unittest.TestCase):
    def test_improved_and_slipped(self):
        prev = scores(story=1, pipeline=3)
        cur = scores(story=3, pipeline=2)
        delta, improved, slipped = jr.compare(prev, cur)
        self.assertEqual(delta, jr.readiness(cur)[0] - jr.readiness(prev)[0])
        self.assertEqual(improved, [("story", "Story", 2)])
        self.assertEqual(slipped, [("pipeline", "Pipeline", 1)])

    def test_no_change(self):
        delta, improved, slipped = jr.compare(scores(), scores())
        self.assertEqual((delta, improved, slipped), (0, [], []))


class EncodeDecodeTest(unittest.TestCase):
    def test_round_trip(self):
        s = scores(story=2, people=4)
        self.assertEqual(jr.decode_scores(jr.encode_scores(s)), s)

    def test_decode_tolerates_garbage(self):
        self.assertEqual(jr.decode_scores(None), scores())
        self.assertEqual(jr.decode_scores("not json"), scores())
        self.assertEqual(jr.decode_scores('[1,2,3]'), scores())
        self.assertEqual(jr.decode_scores('{"story": 99, "junk": 1}'),
                         scores(story=4))


class DbRoundTripTest(unittest.TestCase):
    """The job_readiness_checks table stores and returns a check-in intact."""

    def test_save_and_load_check(self):
        with study_db.temp_study_db():
            con = study_db.connect()
            con.executescript(study_db.STUDY_SCHEMA)
            con.commit()
            con.close()
            s = {k: 2 for k in jr.PILLAR_KEYS}
            pct = jr.readiness(s)[0]
            study_db.db_exec(
                "INSERT INTO job_readiness_checks "
                "(check_date, scores, pct, note, created_at) "
                "VALUES (?,?,?,?,?)",
                ("2026-07-13", jr.encode_scores(s), pct, "first honest look",
                 "2026-07-13T09:00:00"))
            rows = study_db.db_query(
                "SELECT check_date, scores, pct FROM job_readiness_checks")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "2026-07-13")
            self.assertEqual(jr.decode_scores(rows[0][1]), s)
            self.assertEqual(rows[0][2], 50)


if __name__ == "__main__":
    unittest.main()
