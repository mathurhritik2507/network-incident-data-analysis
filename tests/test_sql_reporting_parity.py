"""Offline parity tests for read-only PostgreSQL-compatible reporting queries.

Uses SQLite in memory to execute the three portable SELECT statements against
synthetic CSV rows. This does NOT verify PostgreSQL schema/import execution.
Run: python -m unittest discover -s tests -v
"""

import csv
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "network_incidents.csv"
SQL = ROOT / "sql" / "02_reporting_queries.sql"
RESULTS = ROOT / "results"


class TestSqlReportingParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = "\n".join(
            line for line in SQL.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("--")
        )
        cls.queries = [statement.strip() for statement in text.split(";") if statement.strip()]
        if len(cls.queries) != 3:
            raise AssertionError("Expected exactly three reporting SELECT statements")
        if any(not query.upper().startswith("SELECT") for query in cls.queries):
            raise AssertionError("Reporting queries must be read-only SELECT statements")

        cls.db = sqlite3.connect(":memory:")
        cls.db.row_factory = sqlite3.Row
        cls.db.execute(
            "CREATE TABLE incident_events ("
            "incident_id TEXT, issue_category TEXT, severity TEXT, "
            "resolution_time_minutes INTEGER)"
        )
        with DATA.open(newline="", encoding="utf-8-sig") as handle:
            source_rows = list(csv.DictReader(handle))
        cls.row_count = len(source_rows)
        cls.db.executemany(
            "INSERT INTO incident_events VALUES (?, ?, ?, ?)",
            [
                (row["incident_id"], row["issue_category"], row["severity"],
                 int(row["resolution_time_minutes"]))
                for row in source_rows
            ],
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def check_summary(self, index, filename, group_columns):
        actual = {
            tuple(row[column] for column in group_columns): row
            for row in self.db.execute(self.queries[index])
        }
        with (RESULTS / filename).open(newline="", encoding="utf-8-sig") as handle:
            expected = {
                tuple(row[column] for column in group_columns): row
                for row in csv.DictReader(handle)
            }
        self.assertEqual(set(actual), set(expected), "Group keys differ")
        self.assertEqual(sum(row["incident_count"] for row in actual.values()), self.row_count)
        for key, published in expected.items():
            with self.subTest(group=key):
                self.assertEqual(actual[key]["incident_count"], int(published["incident_count"]))
                self.assertAlmostEqual(
                    actual[key]["avg_resolution_time_minutes"],
                    float(published["avg_resolution_time_minutes"]), places=2,
                )

    def test_category_summary(self):
        self.check_summary(0, "incident_category_summary.csv", ("issue_category",))

    def test_severity_summary(self):
        self.check_summary(1, "severity_summary.csv", ("severity",))

    def test_category_severity_summary(self):
        self.check_summary(
            2, "resolution_time_summary.csv", ("issue_category", "severity")
        )


if __name__ == "__main__":
    unittest.main()
