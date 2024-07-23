import argparse
from main import run_exps

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    ########### Attack model parameters ##########
    parser.add_argument(
        "--attack-model",
        default = "vicuna",
    )
    
    parser.add_argument(
        "--dataset"
    )
    
    parser.add_argument(
        "--target_model",
        default = "vicuna",
        help = "Name of target model.",
        #choices=["vicuna", "llama-2", "gpt-3.5-turbo", "gpt-4", "claude-instant-1","claude-2", "palm-2"]
    )

    parser.add_argument(
        "--countermeasure",
        type = str,
        default = "None",
    )
    
    parser.add_argument(
        "--judge_model",
        type = str,
        default = "gpt-4o-2024-05-13",
    )
    
    parser.add_argument(
        "--attack_type",
        type = str,
        default = "None",
    )
    
    parser.add_argument(
        "--break_task",
        type = str,
        default = "None",
    )
    
    parser.add_argument(
        "--defense_length",
        type = int,
        default = -1,
    )
    
    parser.add_argument(
        "--num_defen_instances",
        type = int
    )

    parser.add_argument(
        "--judge-max-n-tokens",
        type = int,
        default = 10,
        help = "Maximum number of tokens for the judge."
    )
    parser.add_argument(
        "--judge-temperature",
        type=float,
        default=0,
        help="Temperature to use for judge."
    )
    parser.add_argument(
        "--target-max-n-tokens",
        type = int,
        default = 150,
        help = "Maximum number of generated tokens for the target."
    )
    parser.add_argument(
        "--attack-max-n-tokens",
        type = int,
        default = 500,
        help = "Maximum number of generated tokens for the attacker."
    )
    parser.add_argument(
        "--max-n-attack-attempts",
        type = int,
        default = 5,
        help = "Maximum number of attack generation attempts, in case of generation errors."
    )
    ##################################################
    
    # TODO: Add a quiet option to suppress print statement
    
    args = parser.parse_args()
    run_exps(args, [args.countermeasure])
    
    