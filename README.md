# Sentient Analysis Model

Evaluate whether sentiment classifiers rely on an early sentiment-bearing
"trigger word" instead of the sentence context. The dataset contains matched
`conflict`, `agree`, and `context` sentences; the evaluation measures how often
a model follows the trigger word on valid matched triples.

## Requirements

- Python 3
- Internet access for the first real-model run, so Hugging Face checkpoints can
  be downloaded
- Optional: a CUDA-capable GPU. The inference script uses CUDA automatically
  when PyTorch detects it and otherwise runs on the CPU.

## Quick start

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create output directories, then run the complete pipeline with mock models.
This does not download checkpoints or require a GPU, and is the fastest way to
verify the installation:

```powershell
New-Item -ItemType Directory -Force results\predictions, results\tables, results\figures
python -m src.evaluation.run_inference --mock --limit 60
python -m src.evaluation.compute_win_rate --mock
python -m src.stats_analysis --mock
python -m src.plots --mock
```

The commands write mock predictions to `results\predictions`, tables to
`results\tables`, and four PNG figures to `results\figures`. Mock outputs are
only for checking the pipeline; they are not meaningful model results.

## Run the real evaluation

Remove `--mock` to evaluate the configured Hugging Face sentiment classifiers.
The first run downloads model weights and can take substantially longer on a
CPU.

```powershell
New-Item -ItemType Directory -Force results\predictions, results\tables, results\figures
python -m src.evaluation.run_inference
python -m src.evaluation.compute_win_rate
python -m src.stats_analysis
python -m src.plots
```

To run a quick real-model smoke test, limit the number of dataset rows:

```powershell
python -m src.evaluation.run_inference --limit 12
```

By default, inference evaluates every model in `src\models\model_configs.py`.
To evaluate only selected models or adjust batching:

```powershell
python -m src.evaluation.run_inference --models distilbert bert --batch-size 16
```

Before interpreting real results, verify that every checkpoint in
`src\models\model_configs.py` is an SST-2 binary sentiment classifier with the
expected positive-label mapping. The `bert-large` and `roberta-large`
checkpoint selections are specifically marked for verification in that file.

## Outputs

| Location | Contents |
| --- | --- |
| `results\predictions\predictions_<model>.csv` | Per-sentence positive probabilities and predictions |
| `results\tables\triples.csv` | Joined conflict, agree, and context rows for each matched triple |
| `results\tables\win_rate_*.csv` | Overall and factor-level trigger-word win-rate summaries |
| `results\tables\regression_*.csv` | Logistic-regression odds ratios and factor tests, when estimable |
| `results\figures\*.png` | Direction, grid, distance, and validity-check figures |

## Dataset and metric

`data\sentiment_conflict_dataset.csv` is the evaluation target. Its nine fields
are `id`, `base_id`, `condition`, `sentence`, `trigger_word`, `direction`,
`strength`, `distance`, and `true_label`. It contains 300 rows forming 100
matched triples. The four observed `pos-word`/`neg-word` × strong × near/far
cells each contain 25 triples. Weak and mid cells are intentionally absent;
figures display those unavailable positions as `n/a`.

Each `base_id` groups three conditions:

- **conflict**: the trigger word and contextual outcome imply opposite
  sentiment labels.
- **agree**: the trigger word and outcome imply the same label.
- **context**: the outcome alone, without the trigger word.

A triple is valid only when the classifier gets both the `agree` and `context`
sentences correct. For valid triples, the headline **trigger-win rate** is the
share of conflict sentences predicted according to the trigger-word label
rather than the contextual label.

## HPC batch run

`run_inference.slurm` is a Slurm example for GPU inference. Update its
partition, GPU resource name, Conda environment, and any site-specific module
commands before submitting:

```bash
sbatch run_inference.slurm
```

After the batch inference completes, run `compute_win_rate`, `stats_analysis`,
and `plots` from the repository root as shown above.
