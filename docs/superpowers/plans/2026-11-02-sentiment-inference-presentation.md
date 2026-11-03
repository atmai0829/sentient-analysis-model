# Sentiment Inference Presentation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a self-contained Markdown slide deck with speaker notes for a
10-minute academic presentation of the sentiment-trigger inference study.

**Architecture:** Add one root-level `PRESENTATION.md` file. It uses `---` as
slide delimiters, HTML-comment speaker notes, concise source lines, and the
verified real-inference tables as its only numeric authority. It does not
embed external assets, so it remains readable as plain Markdown.

**Tech Stack:** Markdown; existing CSV analysis outputs; Git.

---

## File structure

- Create: `PRESENTATION.md` — the self-contained 10-slide presentation.
- Read: `README.md` — study framing and metric definitions.
- Read: `results/tables/win_rate_overall.csv` — required slide 7 model table.
- Read: `results/tables/regression_odds_ratios.csv` and
  `results/tables/regression_factor_tests.csv` — required slides 8 and 9.
- Read: `src/models/model_configs.py` — model parameter counts.

## Chunk 1: Presentation deck

### Task 1: Write the self-contained slide deck

**Files:**
- Create: `PRESENTATION.md`
- Read: `docs/superpowers/specs/2026-11-02-sentiment-inference-presentation-design.md`

- [ ] **Step 1: Confirm required analysis sources and provenance**

Run:

```powershell
Get-FileHash data\sentiment_conflict_dataset.csv -Algorithm SHA256
git rev-parse HEAD
Get-ChildItem results\predictions\predictions_distilbert.csv, results\predictions\predictions_bert.csv, results\predictions\predictions_roberta.csv, results\predictions\predictions_bert-large.csv, results\predictions\predictions_roberta-large.csv
@'
import pandas as pd
from pathlib import Path
for path in Path("results/predictions").glob("predictions_*.csv"):
    if not path.name.endswith("_mock.csv"):
        assert len(pd.read_csv(path)) == 900, path
print("five 900-row real prediction files confirmed")
'@ | python -
python -m src.evaluation.run_inference  # produces predictions from the hashed dataset
python -m src.evaluation.compute_win_rate  # rebuilds tables from the five files above
python -m src.stats_analysis  # rebuilds regression from results\tables\triples.csv
```

Expected: one dataset SHA-256, one 40-character commit, five real-model
prediction files, and regenerated win-rate and regression tables. Use the
displayed digest and commit as the slide 10 analysis-revision provenance
values; the prediction files must contain 900 rows each, matching the
dataset's 900 rows. The inference command must run after calculating the
digest, establishing that the regenerated tables use that hashed dataset. If
any named prediction file or required table is missing, stop and report the
missing source rather than creating the deck.

- [ ] **Step 2: Create slides 1 through 5**

Create `PRESENTATION.md` with `---` delimiters and HTML-comment notes headed
`Speaker notes:`. Add:

1. The title and research question.
2. The motivation for testing trigger-word reliance.
3. The conflict, agree, and context matched-triple design.
4. The 900-sentence, 300-triple, 12-cell balanced dataset.
5. The five models, valid-triple definition, and trigger-win definition.

Use the approved per-slide note budgets: 40, 50, 60, 60, and 60 seconds. Add
the required `Source: README.md` lines to slides 1 through 3 and 5, and
`Source: data/sentiment_conflict_dataset.csv` to slide 4. State that the
dataset is controlled and synthetic and that the study does not generalize
directly to arbitrary real-world sentiment use.

- [ ] **Step 3: Create slides 6 through 10**

Add:

6. The inference-to-regression analysis pipeline.
7. A table listing all five models with valid triples, trigger-win rate,
   conflict accuracy, and context accuracy.
8. Direction, strength, and distance odds-ratio findings, including the
   `neg-word`, strong, and far reference levels.
9. The parameter-count association, confidence interval, and explicit
   non-causal caveat.
10. Limitations, conclusion, next steps, and the dataset digest plus
   40-character commit provenance.

Use the approved note budgets: 55, 65, 65, 55, and 45 seconds. Add source
lines as follows: slide 6 and 10 use `Source: README.md`; slide 7 uses
`Source: results/tables/win_rate_overall.csv`; slide 8 uses
`Source: results/tables/regression_odds_ratios.csv; results/tables/regression_factor_tests.csv`;
and slide 9 uses `Source: results/tables/regression_odds_ratios.csv;
src/models/model_configs.py`. If the specified figure files exist, append every
listed figure path to its slide's source line, separating paths with `;`.
Round percentages to whole percentages, odds ratios and confidence bounds to
two decimals, and use `< 0.001` for smaller p-values.

- [ ] **Step 4: Verify deck structure and claims**

Run:

```powershell
@'
from pathlib import Path
deck = Path("PRESENTATION.md").read_text(encoding="utf-8")
slides = deck.split("\n---\n")
assert len(slides) == 10
assert all("Speaker notes:" in slide for slide in slides)
expected_sources = (
    "Source: README.md",
    "Source: README.md",
    "Source: README.md",
    "Source: data/sentiment_conflict_dataset.csv",
    "Source: README.md",
    "Source: README.md",
    "Source: results/tables/win_rate_overall.csv",
    "Source: results/tables/regression_odds_ratios.csv; results/tables/regression_factor_tests.csv",
    "Source: results/tables/regression_odds_ratios.csv; src/models/model_configs.py",
    "Source: README.md",
)
assert all(source in slide for source, slide in zip(expected_sources, slides))
for model in ("BERT", "BERT-large", "DistilBERT", "RoBERTa", "RoBERTa-large"):
    assert model in slides[6]
for text in (
    "900", "300", "12",
    "trigger-word label", "valid triple",
    "0.07", "0.16", "1.51",
    "controlled and synthetic", "not generalize",
    "neg-word", "strong", "far",
    "not a causal", "Provenance: dataset SHA-256", "analysis revision",
):
    assert text in deck
print("presentation checks passed")
'@ | python -
```

Expected: `presentation checks passed`.

- [ ] **Step 5: Commit the deck**

```powershell
git add PRESENTATION.md
git commit -m "Add sentiment inference presentation"
```
