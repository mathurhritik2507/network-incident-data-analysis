"""Offline invariants for the synthetic incident daily reporting grain.

Runs without Docker/PostgreSQL: python -m unittest discover -s tests -v
This checks expected grouping behavior, not PostgreSQL execution.
"""
import csv
import sqlite3
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "network_incidents.csv"


class TestDailySummaryGrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with DATA.open(newline="", encoding="utf-8-sig") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.db = sqlite3.connect(":memory:")
        cls.db.execute(
            "CREATE TABLE events (incident_id TEXT PRIMARY KEY, event_time TEXT NOT NULL, "
            "issue_category TEXT NOT NULL, severity TEXT NOT NULL, resolution_minutes INTEGER NOT NULL)"
        )
        cls.db.executemany(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
            [(r["incident_id"], r["date"], r["issue_category"], r["severity"],
              int(r["resolution_time_minutes"])) for r in cls.rows],
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_daily_groups_partition_all_incidents(self):
        groups = self.db.execute(
            "SELECT date(event_time), issue_category, severity, COUNT(*) "
            "FROM events GROUP BY date(event_time), issue_category, severity"
        ).fetchall()
        self.assertTrue(groups, "Expected at least one daily reporting group")
        self.assertEqual(sum(group[3] for group in groups), len(self.rows))
        expected = Counter(
            (r["date"][:10], r["issue_category"], r["severity"]) for r in self.rows
        )
        self.assertEqual({tuple(group[:3]): group[3] for group in groups}, dict(expected))

    def test_daily_average_is_weighted_by_incident_count(self):
        groups = self.db.execute(
            "SELECT date(event_time), issue_category, severity, COUNT(*), "
            "SUM(resolution_minutes) FROM events "
            "GROUP BY date(event_time), issue_category, severity"
        ).fetchall()
        total_minutes = sum(int(r["resolution_time_minutes"]) for r in self.rows)
        self.assertEqual(sum(group[4] for group in groups), total_minutes)
        self.assertAlmostEqual(
            sum(group[4] for group in groups) / sum(group[3] for group in groups),
            total_minutes / len(self.rows),
        )


if __name__ == "__main__":
    unittest.main()
