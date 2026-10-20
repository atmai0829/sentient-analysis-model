"""Compute the trigger-word win rate from saved predictions.

Definitions (per model, per base scenario = one conflict/agree/context triple):
  trigger_win   : the model's prediction on the CONFLICT sentence equals the label
                  the trigger word alone would suggest (= the AGREE label), i.e. it
                  got the conflict sentence wrong in the trigger-word direction.
  valid triple  : the model got BOTH the agree and the context-only versions right.
                  Only then can a conflict-sentence error be blamed on the trigger
                  word rather than on not understanding the context at all.

Headline metric = trigger_win rate among valid triples. We also report the plain
conflict-sentence accuracy and the win rate over ALL triples for transparency.

Usage:  python -m src.evaluation.compute_win_rate [--mock]
"""
import argparse
import glob
import math

import pandas as pd

FACTORS = ["direction", "strength", "distance"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def build_triples(df):
    idx = ["model", "base_id"]
    c = df[df.condition == "conflict"].set_index(idx)
    a = df[df.condition == "agree"].set_index(idx)
    x = df[df.condition == "context"].set_index(idx)
    w = c[["direction", "strength", "distance", "trigger_word", "true_label", "pred", "p_pos"]].rename(
        columns={"true_label": "conflict_label", "pred": "pred_conflict", "p_pos": "p_conflict"})
    w["agree_label"] = a["true_label"]
    w["pred_agree"] = a["pred"]
    w["pred_context"] = x["pred"]
    w = w.reset_index()
    w["agree_ok"] = w.pred_agree == w.agree_label
    w["context_ok"] = w.pred_context == w.conflict_label
    w["valid"] = w.agree_ok & w.context_ok
    w["conflict_correct"] = w.pred_conflict == w.conflict_label
    w["trigger_win"] = w.pred_conflict == w.agree_label
    return w


def summarize(w, by):
    rows = []
    for key, g in w.groupby(by):
        key = key if isinstance(key, tuple) else (key,)
        v = g[g.valid]
        k, n = int(v.trigger_win.sum()), len(v)
        lo, hi = wilson(k, n)
        rows.append({**dict(zip(by, key)),
                     "n_triples": len(g),
                     "n_valid": n,
                     "trigger_win_rate_valid": k / n if n else float("nan"),
                     "ci95_lo": lo, "ci95_hi": hi,
                     "trigger_win_rate_all": g.trigger_win.mean(),
                     "conflict_accuracy": g.conflict_correct.mean(),
                     "agree_accuracy": g.agree_ok.mean(),
                     "context_accuracy": g.context_ok.mean()})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred-glob", default=None)
    ap.add_argument("--out-dir", default="results/tables")
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()

    pattern = args.pred_glob or ("results/predictions/predictions_*_mock.csv" if args.mock
                                 else "results/predictions/predictions_[!_]*.csv")
    files = [f for f in glob.glob(pattern) if args.mock or not f.endswith("_mock.csv")]
    if not files:
        raise SystemExit(f"no prediction files match {pattern}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    w = build_triples(df)
    tag = "_mock" if args.mock else ""
    w.to_csv(f"{args.out_dir}/triples{tag}.csv", index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", lambda v: f"{v:.2f}")
    cols = ["n_valid", "trigger_win_rate_valid", "ci95_lo", "ci95_hi", "conflict_accuracy", "context_accuracy"]

    overall = summarize(w, ["model"])
    overall.to_csv(f"{args.out_dir}/win_rate_overall{tag}.csv", index=False)
    print("\n=== Overall ===\n", overall[["model"] + cols].to_string(index=False))

    for f in FACTORS:
        t = summarize(w, ["model", f])
        t.to_csv(f"{args.out_dir}/win_rate_by_{f}{tag}.csv", index=False)
        print(f"\n=== By {f} ===\n", t[["model", f] + cols].to_string(index=False))

    full = summarize(w, ["model"] + FACTORS)
    full.to_csv(f"{args.out_dir}/win_rate_full_grid{tag}.csv", index=False)
    print(f"\nsaved tables to {args.out_dir}/  (full grid: {len(full)} rows)")


if __name__ == "__main__":
    main()
