"""Run every sentence in the dataset through every model; save per-sentence predictions.

Usage (from the project root):
    python -m src.evaluation.run_inference                       # all models, full dataset
    python -m src.evaluation.run_inference --limit 12            # quick smoke test
    python -m src.evaluation.run_inference --mock --limit 60     # no downloads / no GPU
"""
import argparse
import time

import pandas as pd

from src.models.model_configs import MODELS
from src.models.model_wrapper import load_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/instances.csv")
    ap.add_argument("--out-dir", default="results/predictions")
    ap.add_argument("--models", nargs="+", default=list(MODELS))
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--limit", type=int, default=None, help="only first N rows (testing)")
    ap.add_argument("--mock", action="store_true", help="use fake models (pipeline test only)")
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    if args.limit:
        df = df.head(args.limit)
    print(f"{len(df)} sentences, models: {args.models}")

    for name in args.models:
        t0 = time.time()
        model = load_model(name, mock=args.mock)
        p_pos = model.predict_proba_pos(df["sentence"].tolist(), batch_size=args.batch_size)
        out = df.copy()
        out["model"] = name
        out["p_pos"] = p_pos
        out["pred"] = ["pos" if p >= 0.5 else "neg" for p in p_pos]
        path = f"{args.out_dir}/predictions_{name}{'_mock' if args.mock else ''}.csv"
        out.to_csv(path, index=False)
        print(f"  saved {path}  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
