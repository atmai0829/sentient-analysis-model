"""Figures for the write-up, built from the tables written by compute_win_rate.py.

Usage (project root):
    python -m src.plots            # real results
    python -m src.plots --mock     # plumbing test on mock tables

Figures (results/figures/):
  1_win_rate_by_direction.png   grouped bars, 95% CI           (does direction matter?)
  2_heatmap_grid.png            all 12 cells, one panel/model  (the main figure)
  3_win_rate_vs_distance.png    lines, one per model           (does needed inference matter?)
  4_validity_check.png          context/agree accuracy         (can the win rate be trusted?)
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODEL_ORDER = ["distilbert", "bert", "roberta", "bert-large", "roberta-large"]   # small -> large
COLORS = {"distilbert": "#E69F00", "bert": "#56B4E9", "roberta": "#009E73",
          "bert-large": "#0072B2", "roberta-large": "#CC79A7"}   # colorblind-safe
DIST_ORDER = ["near", "mid", "far"]
RATE, LO, HI = "trigger_win_rate_valid", "ci95_lo", "ci95_hi"


def yerr(d):
    """Asymmetric CI half-widths, clamped at 0 (float rounding can make them -1e-17)."""
    return np.clip(np.array([d[RATE] - d[LO], d[HI] - d[RATE]], dtype=float), 0, None)


def models_in(df):
    return [m for m in MODEL_ORDER if m in set(df.model)] + sorted(set(df.model) - set(MODEL_ORDER))


def fig_direction(tbl, out, tag):
    models = models_in(tbl)
    dirs = ["pos-word", "neg-word"]
    x = np.arange(len(dirs))
    w = 0.8 / len(models)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for i, m in enumerate(models):
        d = tbl[tbl.model == m].set_index("direction").reindex(dirs)
        err = yerr(d)
        ax.bar(x + (i - (len(models) - 1) / 2) * w, d[RATE], w, yerr=err, capsize=3,
               label=m, color=COLORS.get(m))
    ax.set_xticks(x)
    ax.set_xticklabels(["positive word,\nnegative outcome", "negative word,\npositive outcome"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Trigger-win rate (valid triples)")
    ax.set_title("How often the trigger word beats the context" + tag)
    ax.axhline(0.5, ls=":", c="gray", lw=1)
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_heatmap(grid, out, tag):
    models = models_in(grid)
    rows = [("pos-word", "strong"), ("pos-word", "weak"), ("neg-word", "strong"), ("neg-word", "weak")]
    labels = ["pos word / strong", "pos word / weak", "neg word / strong", "neg word / weak"]
    fig, axes = plt.subplots(1, len(models), figsize=(4.2 * len(models), 3.8), sharey=True)
    axes = np.atleast_1d(axes)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#DDDDDD")
    for ax, m in zip(axes, models):
        g = grid[grid.model == m]
        mat = np.full((len(rows), len(DIST_ORDER)), np.nan)
        nmat = np.zeros_like(mat, dtype=int)
        for r, (d, s) in enumerate(rows):
            for c, dist in enumerate(DIST_ORDER):
                cell = g[(g.direction == d) & (g.strength == s) & (g.distance == dist)]
                if len(cell):
                    nmat[r, c] = int(cell.n_valid.iloc[0])
                    if nmat[r, c] > 0:
                        mat[r, c] = cell[RATE].iloc[0]
        im = ax.imshow(np.ma.masked_invalid(mat), vmin=0, vmax=1, cmap=cmap, aspect="auto")
        for r in range(mat.shape[0]):
            for c in range(mat.shape[1]):
                txt = "n/a" if np.isnan(mat[r, c]) else f"{mat[r, c]:.2f}"
                shade = "white" if (not np.isnan(mat[r, c]) and mat[r, c] < 0.6) else "black"
                ax.text(c, r, f"{txt}\n(n={nmat[r, c]})", ha="center", va="center", fontsize=8, color=shade)
        ax.set_xticks(range(len(DIST_ORDER))); ax.set_xticklabels(DIST_ORDER)
        ax.set_yticks(range(len(rows))); ax.set_yticklabels(labels)
        ax.set_xlabel("inference needed"); ax.set_title(m)
    fig.colorbar(im, ax=axes, shrink=0.85, label="trigger-win rate")
    fig.suptitle("Trigger-win rate by cell (n = valid triples)" + tag, y=1.02)
    fig.savefig(out, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_distance(tbl, out, tag):
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(DIST_ORDER))
    for m in models_in(tbl):
        d = tbl[tbl.model == m].set_index("distance").reindex(DIST_ORDER)
        ax.errorbar(x, d[RATE], yerr=yerr(d), marker="o", capsize=3,
                    label=m, color=COLORS.get(m))
    ax.set_xticks(x); ax.set_xticklabels(DIST_ORDER)
    ax.set_xlabel("inference needed to see the context is good/bad")
    ax.set_ylabel("Trigger-win rate (valid triples)")
    ax.set_ylim(0, 1.05); ax.axhline(0.5, ls=":", c="gray", lw=1)
    ax.set_title("Does a harder inference make the trigger word win more?" + tag)
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def fig_validity(overall, out, tag):
    models = models_in(overall)
    metrics = [("context_accuracy", "context-only"), ("agree_accuracy", "agree"), ("conflict_accuracy", "conflict")]
    x = np.arange(len(models)); w = 0.8 / len(metrics)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for i, (col, lab) in enumerate(metrics):
        vals = [overall[overall.model == m][col].iloc[0] for m in models]
        ax.bar(x + (i - 1) * w, vals, w, label=lab)
    ax.set_xticks(x); ax.set_xticklabels(models)
    ax.set_ylim(0, 1.05); ax.set_ylabel("Accuracy")
    ax.set_title("Accuracy by condition (low context-only accuracy = fewer valid triples)" + tag, fontsize=9)
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default="results/tables")
    ap.add_argument("--out-dir", default="results/figures")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    t = "_mock" if a.mock else ""
    tag = " [MOCK DATA]" if a.mock else ""
    fig_direction(pd.read_csv(f"{a.tables}/win_rate_by_direction{t}.csv"), f"{a.out_dir}/1_win_rate_by_direction{t}.png", tag)
    fig_heatmap(pd.read_csv(f"{a.tables}/win_rate_full_grid{t}.csv"), f"{a.out_dir}/2_heatmap_grid{t}.png", tag)
    fig_distance(pd.read_csv(f"{a.tables}/win_rate_by_distance{t}.csv"), f"{a.out_dir}/3_win_rate_vs_distance{t}.png", tag)
    fig_validity(pd.read_csv(f"{a.tables}/win_rate_overall{t}.csv"), f"{a.out_dir}/4_validity_check{t}.png", tag)
    print(f"saved 4 figures to {a.out_dir}/")


if __name__ == "__main__":
    main()
