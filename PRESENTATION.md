# Do Early Sentiment Words Override Context?

## Trigger-word dominance in controlled sentiment conflicts

**Research question:** When an early sentiment-bearing word conflicts with later contextual sentiment, do pretrained SST-2 classifiers follow the trigger word?

Source: README.md

<!-- Speaker notes: (40 seconds) Introduce the central question: whether an early evaluative cue can dominate a model's eventual sentiment decision when later context points in the opposite direction. -->

---

## Motivation

- Sentence classifiers can appear accurate while relying on a salient early lexical cue.
- A sentiment-bearing **trigger word** may override later contextual evidence.
- This controlled synthetic setting tests that mechanism; it **does not establish real-world sentiment behavior**.

Source: README.md

<!-- Speaker notes: (50 seconds) Motivate the study as a diagnostic of shortcut-like lexical reliance. Emphasize that the experiment isolates a mechanism rather than claiming that natural-language sentiment follows the same pattern. -->

---

## Matched sentence triples

For each template and trigger word, construct:

| Member | Role | Expected label |
|---|---|---|
| Agree | Trigger and context align | Shared outcome |
| Conflict | Trigger and context disagree | Contextual outcome |
| Context | Contextual outcome without conflicting trigger | Contextual outcome |

- Matching holds wording and structure as constant as possible.
- The contrast isolates the effect of the conflicting trigger.

Source: README.md

<!-- Speaker notes: (60 seconds) Define the three matched members. The agree item establishes the trigger-consistent label, while the context item establishes the intended contextual label; the conflict item creates the diagnostic disagreement. -->

---

## Controlled dataset design

- **900 sentences** arranged as **300 matched triples**.
- Complete, balanced **2x2x3** grid with **12 balanced factor cells**:
  - trigger direction: positive-word / negative-word
  - trigger strength: strong / weak
  - distance: near / mid / far
- **25 triples per cell**.

Source: data/sentiment_conflict_dataset.csv

<!-- Speaker notes: (60 seconds) Describe the fully crossed design and its balance. There are twelve factor cells, each contributing 25 triples, enabling controlled comparisons of direction, strength, and distance. -->

---

## Models and outcome definitions

- Five pretrained SST-2 classifiers: BERT, BERT-large, DistilBERT, RoBERTa, and RoBERTa-large.
- A triple is **valid** only when agree and context predictions are correct.
- A **trigger win** occurs when the conflict prediction matches the **trigger-word label** (the agree label) rather than the contextual outcome label.

Source: README.md

<!-- Speaker notes: (60 seconds) Explain why validity requires both anchors to be correct: only then is the conflict decision interpretable as a choice between known trigger and context outcomes. Define a trigger win as the conflict prediction selecting the agree label. -->

---

## Analysis pipeline

1. Run model inference on every sentence.
2. Construct matched triples and apply validity filtering.
3. Estimate summary rates and fit clustered logistic regression.

- Clustering accounts for dependence among observations within matched triples.

Source: README.md

<!-- Speaker notes: (55 seconds) Walk through the sequence from raw predictions to matched-triple validity and aggregate rates. Note that clustered logistic regression supports inference while respecting the matched design. -->

---

## Overall model results

| Model | Valid triples | Trigger-win rate | Conflict accuracy | Context accuracy |
|---|---:|---:|---:|---:|
| BERT | 234 | 46% | 45% | 82% |
| BERT-large | 216 | 68% | 26% | 75% |
| DistilBERT | 222 | 57% | 34% | 78% |
| RoBERTa | 249 | 71% | 24% | 83% |
| RoBERTa-large | 254 | 72% | 24% | 85% |

Source: results/tables/win_rate_overall.csv; supporting figure: results/figures/1_win_rate_by_direction.png

<!-- Speaker notes: (65 seconds) Compare models on valid triples. Trigger wins range from 46% to 72%; higher trigger-win rates coincide with lower conflict accuracy, while context accuracy remains substantially higher. -->

---

## Factor effects among valid triples

Reference levels: neg-word, strong, far.

| Factor contrast | Odds ratio (95% CI) | p |
|---|---:|---:|
| Positive-word | 0.07 (0.04-0.11) | < 0.001 |
| Weak | 0.16 (0.10-0.24) | < 0.001 |
| Mid | 1.05 (0.65-1.71) | = 0.836 |
| Near | 1.26 (0.76-2.10) | = 0.368 |

**Direction and strength matter; distance does not.**

Source: results/tables/regression_odds_ratios.csv; results/tables/regression_factor_tests.csv; supporting figures: results/figures/2_heatmap_grid.png; results/figures/3_win_rate_vs_distance.png

<!-- Speaker notes: (65 seconds) Interpret odds relative to negative, strong, and far triggers. Positive and weak triggers sharply reduce trigger-win odds; neither mid nor near distance differs reliably from far distance. -->

---

## Parameter-count association

- Cluster-robust logistic regression on valid triples.
- Odds of a trigger win per parameter doubling: **1.51** (95% CI **1.31-1.74**), **p < 0.001**.
- This association is **not a causal estimate**: architectures and checkpoint training/provenance differ.

Source: results/tables/triples.csv; src/stats_analysis.py; src/models/model_configs.py; supporting figure: results/figures/4_validity_check.png

<!-- Speaker notes: (55 seconds) Report the positive descriptive association with parameter count, then immediately qualify it. Parameter count is entangled with architectural choices and non-identical training and checkpoint provenance. -->

---

## Conclusions, limitations, and next steps

- Early trigger words can dominate later context in this controlled conflict test.
- Limitations: controlled and synthetic dataset; five configured checkpoints; validity filtering.
- Findings do **not generalize** automatically to real-world sentiment behavior.
- Next: test naturalistic counterfactuals, additional model families, and training interventions.

Provenance: dataset SHA-256 2C21EECEB49752CAB33BAADEF3DF2AF1149702522CF0667A817252294AF7BF2A; analysis revision 406970136bcae0814ce6e4bb2a3ca73617c81899

Source: README.md

<!-- Speaker notes: (45 seconds) Conclude with the controlled finding and its boundaries. Reiterate that this is evidence about configured classifiers on synthetic matched examples, then position naturalistic and intervention-based tests as the next steps. -->
