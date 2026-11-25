"""Offline data-contract checks for the synthetic telecom incident CSV.

Run from the repository root with: python -m unittest discover -s tests -v
No database, network, cloud account, or third-party dependencies are required.
"""

import csv
import unittest
from datetime import datetime
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "network_incidents.csv"
EXPECTED_COLUMNS = [
    "incident_id", "date", "device_type", "issue_category", "severity",
    "resolution_time_minutes", "status", "root_cause", "region", "assigned_team",
]
SEVERITIES = {"Low", "Medium", "High", "Critical"}
STATUSES = {"Resolved", "Closed", "Escalated"}


class TestIncidentCsvQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with DATA_PATH.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            cls.columns = reader.fieldnames
            cls.rows = list(reader)

    def test_schema_and_nonempty_dataset(self):
        self.assertEqual(self.columns, EXPECTED_COLUMNS)
        self.assertGreater(len(self.rows), 0)
        self.assertTrue(all(None not in row for row in self.rows), "Unexpected extra CSV fields")

    def test_incident_ids_are_present_and_unique(self):
        ids = [row["incident_id"].strip() for row in self.rows]
        self.assertTrue(all(ids), "Blank incident ID")
        self.assertEqual(len(ids), len(set(ids)), "Duplicate incident IDs")

    def test_timestamps_are_parseable(self):
        for row in self.rows:
            with self.subTest(incident_id=row["incident_id"]):
                datetime.strptime(row["date"], "%Y-%m-%d %H:%M")

    def test_severity_status_and_dimensions(self):
        dimensions = ("device_type", "issue_category", "root_cause", "region", "assigned_team")
        for row in self.rows:
            with self.subTest(incident_id=row["incident_id"]):
                self.assertIn(row["severity"], SEVERITIES)
                self.assertIn(row["status"], STATUSES)
                self.assertTrue(all(row[key] and row[key].strip() for key in dimensions))

    def test_resolution_minutes_are_nonnegative_integers(self):
        for row in self.rows:
            with self.subTest(incident_id=row["incident_id"]):
                minutes = row["resolution_time_minutes"]
                self.assertRegex(minutes, r"^[0-9]+$")
                self.assertGreaterEqual(int(minutes), 0)


if __name__ == "__main__":
    unittest.main()
