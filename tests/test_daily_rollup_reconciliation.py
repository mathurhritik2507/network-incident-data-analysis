"""Offline regression checks for daily incident rollup reconciliation.

Uses only the checked-in simulated CSV and SQLite; this does not execute
PostgreSQL or validate the PostgreSQL view definition.
"""
import csv
from collections import defaultdict
import sqlite3
import unittest
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "network_incidents.csv"


class TestDailyRollupReconciliation(unittest.TestCase):
    def test_daily_groups_preserve_counts_and_resolution_minutes(self):
        with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
            records = list(csv.DictReader(handle))
        self.assertEqual(len(records), 150, "Synthetic fixture size changed")

        db = sqlite3.connect(":memory:")
        try:
            db.execute(
                "CREATE TABLE incidents (incident_day TEXT NOT NULL, "
                "issue_category TEXT NOT NULL, severity TEXT NOT NULL, "
                "resolution_minutes INTEGER NOT NULL)"
            )
            db.executemany(
                "INSERT INTO incidents VALUES (?, ?, ?, ?)",
                [
                    (
                        row["date"][:10],
                        row["issue_category"],
                        row["severity"],
                        int(row["resolution_time_minutes"]),
                    )
                    for row in records
                ],
            )
            groups = db.execute(
                "SELECT incident_day, issue_category, severity, COUNT(*), "
                "SUM(resolution_minutes) FROM incidents "
                "GROUP BY incident_day, issue_category, severity"
            ).fetchall()
            self.assertTrue(groups, "Expected nonempty daily groups")
            expected = defaultdict(lambda: [0, 0])
            for row in records:
                key = (row["date"][:10], row["issue_category"], row["severity"])
                expected[key][0] += 1
                expected[key][1] += int(row["resolution_time_minutes"])
            actual = {
                (day, category, severity): (count, minutes)
                for day, category, severity, count, minutes in groups
            }
            self.assertEqual(
                actual,
                {key: tuple(value) for key, value in expected.items()},
                "Daily SQL groups must match independently aggregated CSV rows",
            )
            self.assertEqual(sum(group[3] for group in groups), len(records))
            self.assertEqual(
                sum(group[4] for group in groups),
                sum(int(row["resolution_time_minutes"]) for row in records),
            )
            self.assertEqual(
                len(groups),
                len({(group[0], group[1], group[2]) for group in groups}),
            )
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
