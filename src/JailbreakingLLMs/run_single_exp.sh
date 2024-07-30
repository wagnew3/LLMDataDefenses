#!/bin/bash
#SBATCH --job-name=myjob
#SBATCH --output=run.out
#SBATCH --error=run.error
#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --time=2:00:00
#SBATCH --gres=gpu:A6000:2
#SBATCH --mem=48G 

# Your job commands go here
#cd /home/wagnew/github/LLMDataDefenses/src/JailbreakingLLMs
# conda activate resist_tor_311

echo "export OPENAI_API_KEY='sk-proj-I576oBGHSiqwLsllEH4mT3BlbkFJpcUAYFzDjAJij5EdOCOW'" >> ~/.zshrc
source ~/.zshrc

python run_exp.py --dataset="wikibios" --attack_type="generate_jailbreaks" --attack-model="finetuned-vicuna" --num_defen_instances=1 --target_model="vicuna" --attack-max-n-tokens=300  #experiment arguements
