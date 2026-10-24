import csv
from collections import Counter, defaultdict
from pathlib import Path
import unittest


DATASET_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "sentiment_conflict_dataset.csv"
)
EXPECTED_FIELDS = [
    "id",
    "base_id",
    "condition",
    "sentence",
    "trigger_word",
    "direction",
    "strength",
    "distance",
    "true_label",
]


class SentimentConflictDatasetTests(unittest.TestCase):
    def test_inference_defaults_to_sentiment_conflict_dataset(self):
        inference_source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "evaluation"
            / "run_inference.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            'default="data/sentiment_conflict_dataset.csv"', inference_source
        )

    def test_dataset_has_expected_schema_and_balanced_factors(self):
        with DATASET_PATH.open(newline="", encoding="utf-8") as dataset_file:
            reader = csv.DictReader(dataset_file)
            rows = list(reader)

        self.assertEqual(EXPECTED_FIELDS, reader.fieldnames)
        self.assertEqual(300, len(rows))

        rows_by_base_id = defaultdict(list)
        for row in rows:
            rows_by_base_id[row["base_id"]].append(row)

        self.assertEqual(100, len(rows_by_base_id))
        for base_id, base_rows in rows_by_base_id.items():
            self.assertEqual(
                {"conflict", "agree", "context"},
                {row["condition"] for row in base_rows},
                base_id,
            )
            self.assertEqual(3, len(base_rows), base_id)

        conflict_factor_counts = Counter(
            (
                row["direction"],
                row["strength"],
                row["distance"],
            )
            for row in rows
            if row["condition"] == "conflict"
        )
        self.assertEqual(
            {
                ("pos-word", "strong", "near"): 25,
                ("pos-word", "strong", "far"): 25,
                ("neg-word", "strong", "near"): 25,
                ("neg-word", "strong", "far"): 25,
            },
            conflict_factor_counts,
        )


if __name__ == "__main__":
    unittest.main()
