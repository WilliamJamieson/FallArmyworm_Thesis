#!/bin/sh

#SBATCH --array=0-200      #Job array start-end
#SBATCH --time=72:00:00    # Run time  hh:mm:22
#SBATCH --mem-per-cpu=6144 # Max memory per cpu in Mb
#SBATCH --job-name=crane_sim_50_gen_no_bt_no_cannib_ad_libitum_only_sus
#SBATCH --mail-type=ALL
#SBATCH --mail-user=wjamieson@huskers.unl.edu
#SBATCH --error=/work/rebarber/wjamieson2/FallArmyworm_Thesis/%x/job_%x.%A_%a.err
#SBATCH --output=/work/rebarber/wjamieson2/FallArmyworm_Thesis/%x/job_%x.%A_%a.out

mkdir -p "$WORK"/FallArmyworm_Thesis/"$SLURM_JOB_NAME"

module load anaconda
conda activate fallarmyworm

python /home/rebarber/wjamieson2/FallArmyworm_Thesis/crane_sim_50_gen_no_bt_no_cannib_ad_libitum_only_sus.py "$SLURM_ARRAY_TASK_ID"
