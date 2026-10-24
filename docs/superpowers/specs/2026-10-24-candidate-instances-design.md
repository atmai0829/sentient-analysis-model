# Candidate Instances Schema and Strong-Conflict Filtering

## Goal

Simplify generated candidate instances by removing their review-status column and
excluding every candidate triple associated with a strong conflict.

## Scope

The generator will:

- Remove `review_status` from the CSV field list and emitted shared values.
- Skip the `conflict`, `agree`, and `context` rows for every strong conflict
  combination.
- Preserve existing IDs for all remaining rows. Removed triples leave gaps in
  `base_id` values by design.

The generated CSV and validator will be updated to match this schema and row
selection.

## Data Flow

`scripts/generate_candidate_instances.py` iterates over direction, strength,
distance, and scenario combinations. Before yielding rows for a combination, it
will skip combinations where the conflict is strong. Other combinations continue
to produce their three-row conflict/agree/context triple.

## Validation

Tests or validation checks will confirm that:

- `review_status` is absent from the generated header and records.
- No retained rows share a `base_id` with a strong conflict triple.
- Every retained `base_id` still has exactly one each of `conflict`, `agree`,
  and `context`.
- The existing validation script accepts the regenerated CSV.

## Error Handling

No new runtime error paths are needed. The existing validator remains the
authority for reporting malformed candidate data.
