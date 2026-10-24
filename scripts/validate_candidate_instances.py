"""Validate the candidate-data schema and matched-triple invariants."""

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "candidate_instances.csv"
FACTORS = {"direction": {"pos-word", "neg-word"}, "strength": {"strong", "weak"},
           "distance": {"near", "mid", "far"}}


def main():
    with DATA.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    errors = []
    triples = defaultdict(list)
    for row in rows:
        triples[row["base_id"]].append(row)
        for factor, allowed in FACTORS.items():
            if row[factor] not in allowed:
                errors.append(f"base_id {row['base_id']}: invalid {factor}")
        if row["review_status"] != "pending":
            errors.append(f"base_id {row['base_id']}: candidate is not pending review")

    counts = Counter()
    for base_id, triple in triples.items():
        by_condition = {row["condition"]: row for row in triple}
        if len(triple) != 3 or set(by_condition) != {"conflict", "agree", "context"}:
            errors.append(f"base_id {base_id}: must contain one conflict, agree, and context row")
            continue
        conflict, agree, context = (by_condition[name] for name in ("conflict", "agree", "context"))
        if conflict["true_label"] != context["true_label"] or conflict["true_label"] == agree["true_label"]:
            errors.append(f"base_id {base_id}: labels do not form a matched triple")
        if not conflict["trigger_word"] or conflict["trigger_word"] != agree["trigger_word"]:
            errors.append(f"base_id {base_id}: conflict and agree must share a trigger word")
        if context["trigger_word"]:
            errors.append(f"base_id {base_id}: context must not contain a trigger word")
        counts[(conflict["direction"], conflict["strength"], conflict["distance"])] += 1

    if set(counts.values()) != {20} or len(counts) != 12:
        errors.append(f"expected 20 triples in each of 12 cells; found {dict(sorted(counts.items()))}")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Valid: {len(rows)} rows, {len(triples)} triples, 20 triples in each factor cell.")


if __name__ == "__main__":
    main()
