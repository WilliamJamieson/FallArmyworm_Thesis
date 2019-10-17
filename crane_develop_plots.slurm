#!/bin/sh

#SBATCH --time=00:20:00
#SBATCH --mem-per-cpu=2048
#SBATCH --job-name=develop_plots
#SBATCH --mail-type=ALL
#SBATCH --mail-user=wjamieson@huskers.unl.edu
#SBATCH --error=/work/rebarber/wjamieson2/FallArmyworm_Thesis/job_%x.%A.err
#SBATCH --output=/work/rebarber/wjamieson2/FallArmyworm_Thesis/job_%x.%A.out

module load anaconda
conda activate fallarmyworm

python /home/rebarber/wjamieson2/FallArmyworm_Thesis/crane_develop_plots.py \
       /work/rebarber/wjamieson2/FallArmyworm_Thesis/develop_plots.html
