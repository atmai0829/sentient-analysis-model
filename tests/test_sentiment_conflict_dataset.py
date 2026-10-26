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

    @classmethod
    def setUpClass(cls):
        with DATASET_PATH.open(newline="", encoding="utf-8") as dataset_file:
            reader = csv.DictReader(dataset_file)
            cls.fieldnames = reader.fieldnames
            cls.rows = list(reader)

        cls.rows_by_base_id = defaultdict(list)
        for row in cls.rows:
            cls.rows_by_base_id[row["base_id"]].append(row)

    def test_dataset_has_expected_header(self):
        self.assertEqual(EXPECTED_FIELDS, self.fieldnames)

    def test_dataset_has_expected_row_and_base_id_counts(self):
        self.assertEqual(900, len(self.rows))
        self.assertEqual(300, len(self.rows_by_base_id))

    def test_ids_and_base_ids_cover_expected_ranges(self):
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(range(1, 901)), {int(value) for value in ids})
        self.assertEqual(
            set(range(1, 301)),
            {int(value) for value in self.rows_by_base_id},
        )

    def test_each_base_id_has_one_row_per_condition_with_shared_factors(self):
        for base_id, base_rows in self.rows_by_base_id.items():
            self.assertEqual(3, len(base_rows), base_id)
            self.assertEqual(
                {"conflict", "agree", "context"},
                {row["condition"] for row in base_rows},
                base_id,
            )
            for factor in ("direction", "strength", "distance"):
                self.assertEqual(
                    1, len({row[factor] for row in base_rows}), (base_id, factor)
                )

    def test_triple_trigger_and_label_relationships(self):
        for base_id, base_rows in self.rows_by_base_id.items():
            by_condition = {row["condition"]: row for row in base_rows}
            conflict = by_condition["conflict"]
            agree = by_condition["agree"]
            context = by_condition["context"]

            self.assertEqual("", context["trigger_word"], base_id)
            self.assertEqual(conflict["true_label"], context["true_label"], base_id)
            self.assertNotEqual(conflict["true_label"], agree["true_label"], base_id)

    def test_conflict_rows_cover_twelve_balanced_factor_cells(self):
        conflict_factor_counts = Counter(
            (row["direction"], row["strength"], row["distance"])
            for row in self.rows
            if row["condition"] == "conflict"
        )
        expected_cells = {
            (direction, strength, distance): 25
            for direction in ("pos-word", "neg-word")
            for strength in ("strong", "weak")
            for distance in ("near", "mid", "far")
        }

        self.assertEqual(12, len(expected_cells))
        self.assertEqual(expected_cells, conflict_factor_counts)


if __name__ == "__main__":
    unittest.main()
