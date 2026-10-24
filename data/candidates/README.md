# Candidate expansion data

`candidate_instances.csv` contains **240 review-pending matched triples**
(720 rows). It adds 20 triples to each factorial cell; together with the 60
triples in `data/raw/instances.csv`, the intended reviewed dataset will contain
25 triples in each of the 12 direction, strength, and distance cells.

These are **candidate labels, not final annotated research data**. Two
independent reviewers should label each sentence without seeing its companion
rows, record their labels in `reviewer_1_label` and `reviewer_2_label`, and
set `annotator_agreement` and `review_status` after adjudication. Remove or
rewrite a triple if either reviewer finds its intended sentiment unclear.

Run this before review or after edits:

```powershell
python scripts\validate_candidate_instances.py
```

After review, merge only accepted triples into `data/raw/instances.csv`; do
not evaluate candidates as final data before that review is complete.
