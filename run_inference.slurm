#!/bin/bash
# Verify the partition / GRES names against hpc.ncsu.edu before submitting (they change).
#SBATCH --job-name=sentiment-eval
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --mem=16GB
#SBATCH --output=results/logs/%j.out
#SBATCH --error=results/logs/%j.err

module load conda
conda activate sentiment-proj
cd "$SLURM_SUBMIT_DIR"

python -m src.evaluation.run_inference
python -m src.evaluation.compute_win_rate
