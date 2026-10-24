import unittest

from scripts import generate_candidate_instances


REVIEW_FIELDS = {
    "annotator_agreement",
    "review_status",
    "reviewer_1_label",
    "reviewer_2_label",
    "review_notes",
}


class CandidateInstancesTests(unittest.TestCase):
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
