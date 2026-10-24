# Single Sentiment Conflict Dataset

## Goal

Use `data/sentiment_conflict_dataset.csv` as the repository's only evaluation
dataset.

## Dataset

The dataset will contain these nine fields:

```text
id,base_id,condition,sentence,trigger_word,direction,strength,distance,true_label
```

`annotator_agreement` will be removed. The file has 300 rows grouped into 100
complete conflict/agree/context triples. It covers four cells: positive and
negative trigger-word directions, each at strong strength and near or far
distance, with 25 triples per cell.

## Application Behavior

`src/evaluation/run_inference.py` will default to
`data/sentiment_conflict_dataset.csv`. The evaluation, statistics, and plotting
code will consume the file through its existing shared fields. Missing weak and
mid cells are intentional; factor summaries and plots will continue to omit
them or render them as unavailable rather than fabricating results.

## Retired Artifacts

Remove the legacy raw/candidate dataset workflow:

- `data/raw/instances.csv`
- `data/candidates/`
- `scripts/generate_candidate_instances.py`
- `scripts/validate_candidate_instances.py`
- Tests specific to the retired candidate/raw schema

The unmerged `merge-candidate-data` branch will be discarded because it only
modifies the retired raw dataset.

## Documentation and Validation

The README will identify the single dataset, its actual four-cell coverage, and
the standard inference pipeline. A replacement standard-library test will
verify the nine-column schema, 300-row/100-triple total, complete triples, and
25 triples in each of the four observed cells.

## Error Handling

The schema test fails explicitly when required fields, complete triples, row
counts, or observed-cell counts are wrong. Existing runtime failures for a
missing data file or invalid model outputs remain unchanged.
