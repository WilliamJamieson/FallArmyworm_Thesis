#!/bin/sh

#SBATCH --array=0-3
#SBATCH --time=00:20:00
#SBATCH --mem-per-cpu=2048
#SBATCH --job-name=test_run
#SBATCH --mail-type=ALL
#SBATCH --mail-user=wjamieson@huskers.unl.edu
#SBATCH --error=/work/rebarber/wjamieson2/FallArmyworm_Thesis/%x/job_%x.%A_%a.err
#SBATCH --output=/work/rebarber/wjamieson2/FallArmyworm_Thesis/%x/job_%x.%A_%a.out

mkdir -p "$WORK"/FallArmyworm_Thesis/"$SLURM_JOB_NAME"

module load anaconda
conda activate fallarmyworm

python /home/rebarber/wjamieson2/FallArmyworm_Thesis/test_run.py "$SLURM_ARRAY_TASK_ID"
