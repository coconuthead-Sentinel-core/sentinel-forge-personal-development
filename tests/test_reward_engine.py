"""Unit tests for lyceum/reward_engine.py — the variable-ratio reward
engine (Reward-Draw board, session 2026-07-16). Headless: temp-file
SQLite via study_db.temp_study_db(), injected rng + clocks, no GUI.

Run from the repo root:   python -m unittest discover -s tests
"""
import random
import unittest
from datetime import datetime, timezone

from lyceum import reward_engine
from lyceum.reward_engine import (EmptyPoolError, RewardService, TIERS,
                                  choose_tier)
from lyceum.db import study_db

NOW = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)

NEVER_RARE = {"STANDARD": 1, "UNCOMMON": 0, "RARE": 0}


class RewardBase(unittest.TestCase):
    def setUp(self):
        self._ctx = study_db.temp_study_db()
        self._ctx.__enter__()
        con = study_db.connect()
        con.executescript(study_db.STUDY_SCHEMA)
        con.commit()
        con.close()

    def tearDown(self):
        self._ctx.__exit__(None, None, None)

    def svc(self, seed=42, **kw):
        service = RewardService(study_db, rng=random.Random(seed), **kw)
        service.seed_default_pool(now=NOW)
        return service


class SchemaTest(RewardBase):
    def test_reward_tables_exist(self):
        names = {r[0] for r in study_db.db_query(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertIn("reward_pool", names)
        self.assertIn("reward_log", names)


class PureKernelTest(unittest.TestCase):
    def test_pity_forces_rare_at_limit(self):
        rng = random.Random(1)
        self.assertEqual(
            choose_tier(11, rng, NEVER_RARE, pity_limit=12), "RARE")

    def test_distribution_tracks_weights(self):
        rng = random.Random(7)
        counts = {t: 0 for t in TIERS}
        drought = 0
        for _ in range(10_000):
            tier = choose_tier(drought, rng)
            counts[tier] += 1
            drought = 0 if tier == "RARE" else drought + 1
        self.assertGreater(counts["STANDARD"], counts["UNCOMMON"])
        self.assertGreater(counts["UNCOMMON"], counts["RARE"])
        self.assertGreater(counts["RARE"], 300)   # ≥3% with pity floor


class PoolHonestyTest(RewardBase):
    def test_unsourced_payload_refused(self):
        service = RewardService(study_db)
        with self.assertRaises(ValueError):
            service.add_pool_entry("UNCOMMON", "a quote", "   ")

    def test_empty_payload_refused(self):
        service = RewardService(study_db)
        with self.assertRaises(ValueError):
            service.add_pool_entry("UNCOMMON", "", "some source")

    def test_bad_tier_refused(self):
        service = RewardService(study_db)
        with self.assertRaises(ValueError):
            service.add_pool_entry("MYTHIC", "quote", "source")

    def test_seed_is_idempotent_and_sourced(self):
        service = RewardService(study_db)
        first = service.seed_default_pool(now=NOW)
        self.assertGreater(first, 0)
        self.assertEqual(service.seed_default_pool(now=NOW), 0)
        for entry in service.pool():
            self.assertTrue(entry["source"].strip())

    def test_every_tier_has_seeded_payloads(self):
        service = self.svc()
        for tier in TIERS:
            self.assertTrue(service.pool(tier=tier),
                            f"no seeded payloads for {tier}")

    def test_retire_is_soft_never_delete(self):
        service = self.svc()
        entry = service.pool(tier="RARE")[0]
        service.retire_pool_entry(entry["pool_id"])
        active = {e["pool_id"] for e in service.pool(tier="RARE")}
        self.assertNotIn(entry["pool_id"], active)
        everything = {e["pool_id"]
                      for e in service.pool(tier="RARE",
                                            include_retired=True)}
        self.assertIn(entry["pool_id"], everything)


class DrawTest(RewardBase):
    def test_no_event_no_reward(self):
        service = self.svc()
        for bad in ("", "   ", None):
            with self.assertRaises(ValueError):
                service.draw(bad, now=NOW)
        self.assertEqual(service.history(), [])

    def test_empty_pool_raises(self):
        service = RewardService(study_db)   # unseeded
        with self.assertRaises(EmptyPoolError):
            service.draw("focus block", now=NOW)

    def test_reward_carries_named_source(self):
        reward = self.svc().draw("focus block 25 min", now=NOW)
        self.assertIn(reward.tier, TIERS)
        self.assertTrue(reward.payload.strip())
        self.assertTrue(reward.source.strip())

    def test_pity_guarantees_rare_within_limit(self):
        service = self.svc(seed=1, weights=NEVER_RARE, pity_limit=5)
        tiers = [service.draw(f"block {i}", now=NOW).tier
                 for i in range(1, 11)]
        self.assertEqual(tiers[4], "RARE")
        self.assertEqual(tiers[9], "RARE")
        self.assertTrue(all(t == "STANDARD" for t in tiers[:4]))

    def test_drought_survives_restart(self):
        first = self.svc(seed=1, weights=NEVER_RARE, pity_limit=10)
        for i in range(3):
            first.draw(f"block {i}", now=NOW)
        self.assertEqual(first.drought(), 3)
        # A brand-new service over the same DB remembers the drought —
        # the pity counter lives in the append-only log, not in memory.
        second = RewardService(study_db, rng=random.Random(2),
                               weights=NEVER_RARE, pity_limit=10)
        self.assertEqual(second.drought(), 3)

    def test_history_append_only_and_ordered(self):
        service = self.svc()
        for i in range(5):
            service.draw(f"block {i}", now=NOW)
        events = [h["event"] for h in service.history()]
        self.assertEqual(events, [f"block {i}" for i in reversed(range(5))])
        self.assertEqual(len(service.history()), 5)


if __name__ == "__main__":
    unittest.main()
