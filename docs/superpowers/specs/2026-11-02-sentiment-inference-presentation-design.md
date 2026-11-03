# Sentiment Inference Presentation Design

## Purpose

Create a self-contained Markdown presentation for a 10-minute academic talk
about the Sentient Analysis Model project. The presentation explains the
research question, controlled dataset design, inference pipeline, results,
limitations, and implications.

## Audience and format

- Audience: academic.
- Duration: approximately 10 minutes.
- Format: renderer-neutral slide-oriented Markdown. Separate slides with `---`.
  Put speaker notes in HTML comments headed `Speaker notes:`; the document
  remains useful as a plain Markdown outline if a renderer does not expose
  notes. Do not embed or link images: the Markdown must remain self-contained.
- Narrative: research question, controlled experiment, evidence, and
  implications.
- Timing: use speaking budgets of 40, 50, 60, 60, 60, 55, 65, 65, 55, and 45
  seconds for slides 1 through 10, respectively. This totals 9 minutes 15
  seconds and leaves time for transitions.

## Slide structure

1. Title and research question.
2. Motivation for testing trigger-word reliance.
3. Matched conflict, agree, and context triples.
4. Dataset composition and balanced factor grid.
5. Models, validity filter, and trigger-win metric.
6. Inference and analysis pipeline.
7. Overall model results.
8. Direction, strength, and distance effects.
9. Model-size result and interpretation.
10. Limitations, conclusion, and next steps.

## Content requirements

- Use the current real-inference results from `results/tables`.
- Cite the relevant generated figure path in a source line where it reinforces
  a result, but present all claims as text or tables so no figure asset is
  required to read the deck.
- State that the dataset is controlled and synthetic; do not generalize its
  results to arbitrary real-world sentiment use.
- Define a valid triple as one where both agree and context conditions are
  correct before reporting the trigger-win rate.
- Define a trigger win as a conflict-sentence prediction that matches the
  trigger-word label (the agree-condition label) rather than the contextual
  outcome label.
- Include concise on-slide content and presenter notes calibrated to the
  per-slide timing budget.
- Round percentages to whole percentages and odds ratios to two decimals,
  unless a confidence interval is included; report confidence intervals to two
  decimals and p-values as `< 0.001` when applicable.
- Add a short source line to slides 4 and 7 through 9 that report numeric
  results. Use the source-line template `Source: <project-relative paths>;
  supporting figure: <project-relative path>` when a listed supporting figure
  exists, otherwise omit the figure clause.
- Use `Source: README.md` on slides 1 through 3, 5 through 6, and 10 because
  those slides communicate the study framing, method, or implications rather
  than a numeric result.
- Slide 7 must include all five models with valid-triple count, trigger-win
  rate, conflict accuracy, and context accuracy. Slide 8 must report the
  direction, strength, and distance regression results. Slide 9 must report
  the model-size association and its non-causal caveat.

## Result sources

| Slides | Source | Values |
| --- | --- | --- |
| 4 | `data/sentiment_conflict_dataset.csv` | 900 sentences, 300 triples, and 12 balanced factor cells |
| 7 | `results/tables/win_rate_overall.csv` | Per-model valid-triple count, trigger-win rate, conflict accuracy, and context accuracy |
| 8 | `results/tables/regression_odds_ratios.csv` and `results/tables/regression_factor_tests.csv` | Direction, strength, and distance effects |
| 9 | `results/tables/regression_odds_ratios.csv` and `src/models/model_configs.py` | Association between parameter count and trigger following; approximate parameter counts: 66M, 110M, 125M, 340M, and 355M |

Figures are optional supporting material; a missing figure must not suppress a
claim supported by its named table. A missing required table must suppress the
affected claim rather than imply a current result. If any required table is
missing, stop creation and report the missing source instead of producing an
incomplete presentation.

## Figure references

| Slide | Optional supporting figure |
| --- | --- |
| 7 | `results/figures/1_win_rate_by_direction.png` |
| 8 | `results/figures/2_heatmap_grid.png` and `results/figures/3_win_rate_vs_distance.png` |
| 9 | `results/figures/4_validity_check.png` |

Mention the listed file path in the slide's source line only when the file
exists; separate multiple figure paths with `;`. Do not make a figure reference
on other slides.

## Regression interpretation

The outcome is `trigger_win` among valid triples. The categorical-regression
reference levels are `neg-word` direction, `strong` strength, `far` distance,
and `bert` model. Slides 8 and 9 must describe odds ratios relative to these
levels. Slide 9 may report the parameter-count association, but must state
that it is not a causal architecture-size effect because checkpoint training
and architecture also differ.

## Data flow and validation

The presentation derives its numeric claims from the full-dataset inference
outputs: `results/predictions/predictions_{distilbert,bert,roberta,bert-large,
roberta-large}.csv`. They were produced by
`python -m src.evaluation.run_inference` against
`data/sentiment_conflict_dataset.csv`, then summarized by
`python -m src.evaluation.compute_win_rate` and
`python -m src.stats_analysis`. The current presentation must include the
dataset's SHA-256 digest and the current 40-character Git commit in a
provenance line on slide 10: `Provenance: dataset SHA-256 <digest>; analysis
revision <commit>`. The analysis revision is the 40-character `HEAD` commit
recorded when the result sources are verified, before the presentation is
committed; it identifies the project state that produced the claims.

The existing test suite verifies dataset structure and factor-grid balance. The
presentation will preserve reported values rather than recalculating or
modifying project data. Before creating the deliverable, run
`python -m src.evaluation.compute_win_rate` after confirming all five named
prediction files exist, then run `python -m src.stats_analysis`; this rebuilds
the required tables from those predictions. Confirm that the dataset digest
recorded in the deck is calculated from the dataset used by
`run_inference`. If any command or required source is unavailable, stop and
report the missing prerequisite rather than producing the presentation.

## Deliverable

Add one root-level Markdown file named `PRESENTATION.md`. It will be readable
as an outline and portable to a Markdown slide renderer, while retaining notes
for an oral academic presentation.
