# Candidate Instances Review-Status Removal

## Goal

Simplify generated candidate instances by removing their review-status column.

## Scope

The generator will:

- Remove `review_status` from the CSV field list and emitted shared values.

The generated CSV and validator will be updated to match the reduced schema.
No rows, triples, or `base_id` values will be deleted, renumbered, or selected
by word strength. The user will separately delete the relevant `base_id`
triples after inspecting conflicts such as ID 181, which contains both
“thrilled” and “rejected.”

## Data Flow

`scripts/generate_candidate_instances.py` iterates over direction, strength,
distance, and scenario combinations, producing each conflict/agree/context
triple unchanged. It omits `review_status` when creating the CSV header and
records.

## Validation

Tests or validation checks will confirm that:

- `review_status` is absent from the generated header and records.
- Every retained `base_id` still has exactly one each of `conflict`, `agree`,
  and `context`.
- There are 20 triples in each of the 12 direction/strength/distance factor
  cells.
- The existing validation script accepts the regenerated CSV.

## Error Handling

No new runtime error paths are needed. The existing validator remains the
authority for reporting malformed candidate data.
