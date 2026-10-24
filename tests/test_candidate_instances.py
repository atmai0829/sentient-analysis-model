import csv
from pathlib import Path
import unittest

from scripts import generate_candidate_instances


RAW_INSTANCES_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "raw" / "instances.csv"
)


REVIEW_FIELDS = {
    "annotator_agreement",
    "review_status",
    "reviewer_1_label",
    "reviewer_2_label",
    "review_notes",
}


class CandidateInstancesTests(unittest.TestCase):
    def test_raw_rows_omit_annotator_agreement(self):
        with RAW_INSTANCES_PATH.open(newline="", encoding="utf-8") as raw_file:
            reader = csv.DictReader(raw_file)
            rows = list(reader)

        self.assertNotIn("annotator_agreement", reader.fieldnames)
        self.assertEqual(180, len(rows))
        self.assertTrue(
            all("annotator_agreement" not in row for row in rows)
        )

    def test_generated_rows_omit_review_fields(self):
        self.assertTrue(
            REVIEW_FIELDS.isdisjoint(generate_candidate_instances.FIELDS)
        )

        generated_rows = list(generate_candidate_instances.rows())

        self.assertTrue(generated_rows)
        self.assertTrue(
            all(REVIEW_FIELDS.isdisjoint(row) for row in generated_rows)
        )


if __name__ == "__main__":
    unittest.main()
