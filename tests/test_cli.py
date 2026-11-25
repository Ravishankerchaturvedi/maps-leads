import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
HEADER = "name,category,phone,website,address,city,rating,reviews"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "maps_leads", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class CliTests(unittest.TestCase):
    def test_clean_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli(
                "clean",
                str(FIXTURES / "gosom_sample.csv"),
                "-o",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = output.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], HEADER)
            with output.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(len(row) == 8 for row in rows))
            self.assertEqual(rows[0]["name"], "Spice Garden")
            self.assertEqual(rows[0]["phone"], "+919876543210")
            self.assertEqual(rows[0]["website"], "https://www.spicegarden.example")
            self.assertEqual(rows[0]["city"], "Bengaluru")
            self.assertEqual(rows[0]["rating"], "4.5")
            self.assertEqual(rows[0]["reviews"], "1234")
            self.assertIn("in: 7", result.stderr)
            self.assertIn("out: 4", result.stderr)
            self.assertIn("dropped_duplicate: 2", result.stderr)
            self.assertIn("dropped_no_name: 1", result.stderr)

    def test_clean_jsonl(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli(
                "clean",
                str(FIXTURES / "gosom_sample.jsonl"),
                "-o",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["name"], "Third Wave Coffee")
            self.assertEqual(rows[0]["website"], "https://www.thirdwave.example")
            self.assertEqual(rows[2]["category"], "Modern Indian restaurant")
            self.assertIn("in: 5", result.stderr)
            self.assertIn("out: 3", result.stderr)
            self.assertIn("dropped_duplicate: 1", result.stderr)
            self.assertIn("dropped_no_name: 1", result.stderr)

    def test_clean_json_array(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli(
                "clean",
                str(FIXTURES / "gosom_sample_array.json"),
                "-o",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["website"], "https://www.kolkatakati.example")
            self.assertEqual(rows[0]["city"], "Kolkata")
            self.assertEqual(rows[1]["city"], "Pune")

    def test_min_reviews_filter(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli(
                "clean",
                str(FIXTURES / "gosom_sample.csv"),
                "-o",
                str(output),
                "--min-reviews",
                "100",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["name"] for row in rows], ["Spice Garden", "Chennai Silks"])
            self.assertIn("filtered: 3", result.stderr)
            self.assertIn("out: 2", result.stderr)
            self.assertIn("dropped_duplicate: 1", result.stderr)

    def test_no_website_filter(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli(
                "clean",
                str(FIXTURES / "gosom_sample.csv"),
                "-o",
                str(output),
                "--no-website",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                [row["name"] for row in rows],
                ["Spice Garden MG Road", "Spice Garden", "Blue Tokai Coffee"],
            )
            self.assertIn("filtered: 3", result.stderr)

    def test_has_website_filter(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli(
                "clean",
                str(FIXTURES / "gosom_sample.csv"),
                "-o",
                str(output),
                "--has-website",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                [row["name"] for row in rows],
                ["Spice Garden", "Mumbai Tiffin", "Chennai Silks"],
            )
            self.assertIn("filtered: 3", result.stderr)

    def test_missing_input_returns_error(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "leads.csv"
            result = run_cli("clean", str(FIXTURES / "missing.csv"), "-o", str(output))
            self.assertEqual(result.returncode, 2)
            self.assertIn("cannot read", result.stderr)


if __name__ == "__main__":
    unittest.main()
