#!/bin/bash
#SBATCH --job-name=myjob
#SBATCH --output=%j-output.out
#SBATCH --error=%j-output.err
#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --time=2:00:00
#SBATCH --gres=gpu:a6000:1 

# Your job commands go here
cd /home/wagnew/github/LLMDataDefenses/src/JailbreakingLLMs
conda activate resist_tor_311

python run_exp.py --attack-model="$1" --dataset="$2" --target_model="$3" --countermeasure="$4" --judge_model="$5" --attack_type="$6" --break_task="$7" --defense_length=$8 --num_defen_instances=$9
