# Candidate expansion data

`candidate_instances.csv` contains **240 candidate matched triples** (720
rows). It adds 20 triples to each factorial cell; together with the 60 raw
triples in `data/raw/instances.csv`, the combined dataset contains 25 triples
in each of the 12 direction, strength, and distance cells.

Candidates are **not final data**. Manually inspect them and remove or rewrite
any triple whose intended sentiment is unclear.

Run this after edits:

```powershell
python scripts\validate_candidate_instances.py
```

Merge only accepted triples into `data/raw/instances.csv` after inspection; do
not evaluate candidates as final data before they are added there.
