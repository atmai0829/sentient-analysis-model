"""Create candidate triples to expand the raw dataset to 25 triples per cell."""

import csv
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "candidates" / "candidate_instances.csv"
PER_CELL = 20  # The raw dataset already provides five triples in every cell.

SCENARIOS = [
    ("my scholarship application", "The committee funded the full year.", "The committee rejected it after the deadline."),
    ("my apartment application", "The landlord approved it the same day.", "The landlord gave the unit to someone else."),
    ("my package delivery", "The courier left it safely at my door.", "The courier sent it to the wrong address."),
    ("my dental appointment", "The dentist said everything looked healthy.", "The dentist found a painful infection."),
    ("my train reservation", "The train arrived early at my stop.", "The train was canceled before departure."),
    ("my job interview", "The manager offered me the position.", "The manager said they had chosen another candidate."),
    ("my phone repair", "The technician fixed it under warranty.", "The technician said the repair would cost more than a new phone."),
    ("my course registration", "I got every class I needed.", "Every required class was already full."),
    ("my insurance claim", "The insurer approved the payment.", "The insurer denied the claim."),
    ("my vacation rental", "The host upgraded us to a larger room.", "The host canceled the reservation on arrival."),
    ("my grant proposal", "The panel awarded the requested funding.", "The panel declined to fund the proposal."),
    ("my car service", "The mechanic finished the repair for free.", "The mechanic found a costly engine problem."),
    ("my library hold", "The book arrived before my deadline.", "The library canceled the hold without notice."),
    ("my concert tickets", "The venue moved us to better seats.", "The venue voided the tickets at the gate."),
    ("my internship application", "The coordinator invited me to join the team.", "The coordinator closed the role before reviewing my application."),
    ("my grocery delivery", "Every item arrived fresh and complete.", "Several items arrived spoiled and missing."),
    ("my passport renewal", "The passport arrived before my trip.", "The passport arrived after my flight had left."),
    ("my utility bill", "The company corrected the overcharge.", "The company doubled the bill by mistake."),
    ("my exam appeal", "The department restored the missing points.", "The department rejected the appeal."),
    ("my moving appointment", "The movers finished ahead of schedule.", "The movers damaged several boxes."),
]

TRIGGERS = {
    ("pos-word", "strong"): ("I was thrilled about {subject}", "thrilled"),
    ("pos-word", "weak"): ("I was glad about {subject}", "glad"),
    ("neg-word", "strong"): ("I dreaded {subject}", "dreaded"),
    ("neg-word", "weak"): ("I was worried about {subject}", "worried"),
}

DISTANCE_FILLER = {
    "near": "",
    "mid": " I checked the details later that afternoon.",
    "far": " The next morning, I reviewed my schedule, called a friend, and made coffee before reading the final update.",
}

FIELDS = [
    "id", "base_id", "condition", "sentence", "trigger_word", "direction",
    "strength", "distance", "true_label",
]


def make_sentence(trigger, subject, outcome, distance):
    return f"{trigger.format(subject=subject)}.{DISTANCE_FILLER[distance]} {outcome}"


def rows():
    row_id, base_id = 181, 61
    for direction, strength, distance in product(
        ("pos-word", "neg-word"), ("strong", "weak"), ("near", "mid", "far")
    ):
        trigger, trigger_word = TRIGGERS[(direction, strength)]
        for subject, positive, negative in SCENARIOS[:PER_CELL]:
            conflict_outcome, agree_outcome = (
                (negative, positive) if direction == "pos-word" else (positive, negative)
            )
            conflict_label, agree_label = (
                ("neg", "pos") if direction == "pos-word" else ("pos", "neg")
            )
            shared = {
                "base_id": base_id,
                "trigger_word": trigger_word,
                "direction": direction,
                "strength": strength,
                "distance": distance,
            }
            yield {
                **shared, "id": row_id, "condition": "conflict",
                "sentence": make_sentence(trigger, subject, conflict_outcome, distance),
                "true_label": conflict_label,
            }
            yield {
                **shared, "id": row_id + 1, "condition": "agree",
                "sentence": make_sentence(trigger, subject, agree_outcome, distance),
                "true_label": agree_label,
            }
            yield {
                **shared, "id": row_id + 2, "condition": "context",
                "sentence": conflict_outcome, "trigger_word": "", "true_label": conflict_label,
            }
            row_id += 3
            base_id += 1


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows())
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
