#!/bin/bash
#SBATCH --job-name=myjob
#SBATCH --output=run.out
#SBATCH --error=run.error
#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --time=2:00:00
#SBATCH --gres=gpu:A6000:1
#SBATCH --mem=48G 

# Your job commands go here
cd /home/wagnew/github/LLMDataDefenses/src/JailbreakingLLMs
conda activate resist_tor_311

python run_exp.py #experiment arguements
