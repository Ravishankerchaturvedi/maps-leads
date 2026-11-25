import unittest
from pathlib import Path

from maps_leads.readers import detect_format, read_rows

FIXTURES = Path(__file__).parent / "fixtures"


class ReaderTests(unittest.TestCase):
    def test_detect_csv(self):
        self.assertEqual(detect_format("input_id,link,title\n1,x,Cafe\n"), "csv")

    def test_detect_json_array(self):
        self.assertEqual(detect_format('[{"title": "Cafe"}]'), "json")

    def test_detect_jsonl(self):
        self.assertEqual(detect_format('{"title": "Cafe"}\n{"title": "Shop"}\n'), "json")

    def test_read_gosom_csv(self):
        rows = read_rows(FIXTURES / "gosom_sample.csv")
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0]["title"], "Spice Garden")
        self.assertEqual(rows[0]["review_rating"], "4.500000")

    def test_read_gosom_jsonl(self):
        rows = read_rows(FIXTURES / "gosom_sample.jsonl")
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["title"], "Third Wave Coffee")
        self.assertEqual(rows[0]["web_site"], "https://WWW.ThirdWave.example/about")

    def test_read_gosom_json_array(self):
        rows = read_rows(FIXTURES / "gosom_sample_array.json")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["title"], "Kolkata Kati Roll")

    def test_forced_csv_format(self):
        rows = read_rows(FIXTURES / "gosom_sample.csv", fmt="csv")
        self.assertEqual(rows[0]["title"], "Spice Garden")

    def test_forced_json_format(self):
        rows = read_rows(FIXTURES / "gosom_sample.jsonl", fmt="json")
        self.assertEqual(rows[0]["title"], "Third Wave Coffee")


if __name__ == "__main__":
    unittest.main()
