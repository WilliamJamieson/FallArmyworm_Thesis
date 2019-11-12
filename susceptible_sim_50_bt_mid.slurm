#!/bin/sh

#SBATCH --array=0-199      #Job array start-end
#SBATCH --time=96:00:00    # Run time  hh:mm:ss
#SBATCH --mem-per-cpu=6144 # Max memory per cpu in Mb
#SBATCH --job-name=susceptible_sim_50_bt_mid
#SBATCH --mail-type=ALL
#SBATCH --mail-user=wjamieson@huskers.unl.edu
#SBATCH --error=/work/rebarber/wjamieson2/FallArmyworm_Thesis/job_%x.%A_%a.err
#SBATCH --output=/work/rebarber/wjamieson2/FallArmyworm_Thesis/job_%x.%A_%a.out

module load anaconda
conda activate fallarmyworm

python /home/rebarber/wjamieson2/FallArmyworm_Thesis/"$SLURM_JOB_NAME".py "$SLURM_ARRAY_TASK_ID"
