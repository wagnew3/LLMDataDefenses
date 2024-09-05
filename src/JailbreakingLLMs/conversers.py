import common
from language_models import GPT, Claude, PaLM, HuggingFace, FinetunedCheckpoint
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import VICUNA_PATH, LLAMA_PATH, ATTACK_TEMP, TARGET_TEMP, ATTACK_TOP_P, TARGET_TOP_P   
import os

def load_attack_and_target_models(args):
    # Load attack model and tokenizer
    #print("args.attack_model", args.attack_model)
    print("MAX_TOKENS:", args.attack_max_n_tokens)
    attackLM = AttackLM(model_name = args.attack_model, 
                        max_n_tokens = args.attack_max_n_tokens, 
                        max_n_attack_attempts = args.max_n_attack_attempts, 
                        temperature = ATTACK_TEMP, # init to 1
                        top_p = ATTACK_TOP_P, # init to 0.9
                        attack_type=args.attack_type
                        )
    preloaded_model = None
    if args.attack_model == args.target_model:
        #print("Using same attack and target model. Using previously loaded model.")
        preloaded_model = attackLM.model
    targetLM = TargetLM(model_name = args.target_model, 
                        max_n_tokens = args.target_max_n_tokens,
                        temperature = TARGET_TEMP, # init to 0
                        top_p = TARGET_TOP_P, # init to 1
                        preloaded_model = preloaded_model,
                        )
    return attackLM, targetLM

class AttackLM():
    """
        Base class for attacker language models.
        
        Generates attacks for conversations using a language model. The self.model attribute contains the underlying generation model.
    """
    def __init__(self, 
                model_name: str, 
                max_n_tokens: int, 
                max_n_attack_attempts: int, 
                temperature: float,
                top_p: float,
                attack_type):
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_n_tokens = max_n_tokens
        self.max_n_attack_attempts = max_n_attack_attempts
        self.top_p = top_p
        self.model, self.template = load_indiv_model(model_name)
        if attack_type=="original":
            self.attack_keys=["prompt", "improvement"]
        else:
            self.attack_keys=["prompt"]
        
        if ("vicuna" in model_name or "llama" in model_name) and not "finetuned" in model_name:
            self.model.extend_eos_tokens()



    def get_attack(self, convs_list, prompts_list):
        """
        Generates responses for a batch of conversations and prompts using a language model. 
        Only valid outputs in proper JSON format are returned. If an output isn't generated 
        successfully after max_n_attack_attempts, it's returned as None.
        
        Parameters:
        - convs_list: List of conversation objects.
        - prompts_list: List of prompts corresponding to each conversation.
        
        Returns:
        - List of generated outputs (dictionaries) or None for failed generations.
        """
        
        conv = convs_list[0]
        prompt = prompts_list[0]
        
        init_message = """{\"improvement\": \"\",\"prompt\": \"""" if len(conv.messages) == 0 else """{\"improvement\": \""""

        conv.append_message(conv.roles[0], prompt)

        if "gpt" in self.model_name or "claude" in self.model_name or "gemini" in self.model_name:
            full_prompt = conv.to_openai_api_messages()
        else:
            conv.append_message(conv.roles[1], init_message)
            current_prompt = conv.get_prompt()
            if not conv.sep2 is None:
                current_prompt = current_prompt[:-len(conv.sep2)]
            full_prompt = current_prompt

        start_time = time.time()
        full_output = self.model.generate(full_prompt,
                                     max_n_tokens = self.max_n_tokens,  
                                     temperature = self.temperature,
                                     top_p = self.top_p
                                    )
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Time used:", elapsed_time)

        full_output=full_output.replace("\\n", "\n")

        print("PROMPT:", full_output)
        return [{'prompt': full_output}]

        """
        Code below is deprecated
        """
        # assert len(convs_list) == len(prompts_list), "Mismatch between number of conversations and prompts."
        
        # batchsize = len(convs_list)
        # indices_to_regenerate = list(range(batchsize))
        # valid_outputs = [None] * batchsize

        # # Initalize the attack model's generated output to match format
        # if len(convs_list[0].messages) == 0:
        #     init_message = """{\"improvement\": \"\",\"prompt\": \""""
        # else:
        #     init_message = """{\"improvement\": \"""" 

        # full_prompts = []
        # # Add prompts and initial seeding messages to conversations (only once)
        # for conv, prompt in zip(convs_list, prompts_list):
        #     conv.append_message(conv.roles[0], prompt)
        #     # Get prompts
        #     if "gpt" in self.model_name or "claude" in self.model_name or "gemini" in self.model_name:
        #         full_prompts.append(conv.to_openai_api_messages())
        #     else:
        #         conv.append_message(conv.roles[1], init_message)
                
        #         current_prompt = conv.get_prompt()
        #         if not conv.sep2 is None:
        #             current_prompt = current_prompt[:-len(conv.sep2)]
        #         full_prompts.append(current_prompt)
            
        # for attempt in range(self.max_n_attack_attempts):
        #     # Subset conversations based on indices to regenerate
        #     full_prompts_subset = [full_prompts[i] for i in indices_to_regenerate]

        #     # Generate outputs 
        #     start_time = time.time()
        #     outputs_list = self.model.batched_generate(full_prompts_subset,
        #                                                 max_n_tokens = self.max_n_tokens,  
        #                                                 temperature = self.temperature,
        #                                                 top_p = self.top_p
        #                                             )
        #     end_time = time.time()
        #     elapsed_time = end_time - start_time
        #     print("Time used:", elapsed_time)

        #     # Check for valid outputs and update the list
        #     new_indices_to_regenerate = []
        #     for i, full_output in enumerate(outputs_list):
        #         orig_index = indices_to_regenerate[i]
        #         # if "gpt" not in self.model_name and 'claude' not in self.model_name and "gemini" not in self.model_name:
        #         #     full_output = init_message + full_output
        #         full_output=full_output.replace("\\n", "\n")
        #         print("PROMPT:", full_output)
        #         #attack_dict, json_str = common.extract_json(full_output, expected_keys=self.attack_keys)
        #         return [{'prompt': full_output}]

                
        # #         if attack_dict is not None:
        # #             valid_outputs[orig_index] = attack_dict
        # #             convs_list[orig_index].update_last_message(json_str)  # Update the conversation with valid generation
        # #         else:
        # #             new_indices_to_regenerate.append(orig_index)
        # #
        # #     # Update indices to regenerate for the next iteration
        # #     indices_to_regenerate = new_indices_to_regenerate
        # #
        # #     # If all outputs are valid, break
        # #     if not indices_to_regenerate:
        # #         break
        # #
        # # if any([output for output in valid_outputs if output is None]):
        # #     print(f"Failed to generate output after {self.max_n_attack_attempts} attempts. Terminating.")
        # # return valid_outputs

class TargetLM():
    """
        Base class for target language models.
        
        Generates responses for prompts using a language model. The self.model attribute contains the underlying generation model.
    """
    def __init__(self, 
            model_name: str, 
            max_n_tokens: int, 
            temperature: float,
            top_p: float,
            preloaded_model: object = None):
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_n_tokens = max_n_tokens
        self.top_p = top_p
        if preloaded_model is None:
            self.model, self.template = load_indiv_model(model_name)
        else:
            self.model = preloaded_model
            _, self.template = get_model_path_and_template(model_name)

    def get_response(self, prompts_list, break_task):
        batchsize = len(prompts_list)
        convs_list = [common.conv_template(self.template) for _ in range(batchsize)]
        full_prompts = []
        for conv, prompt in zip(convs_list, prompts_list):
            conv.append_message(conv.roles[0], prompt)
            if "gpt" in self.model_name or "claude" in self.model_name or "gemini" in self.model_name:
                # Openai does not have separators
                full_prompts.append(conv.to_openai_api_messages())
            elif "palm" in self.model_name:
                full_prompts.append(conv.messages[-1][1])
            else:
                conv.append_message(conv.roles[1], None) 
                full_prompts.append(conv.system_message+" "+break_task+" "+prompts_list[0])
        
        if "gpt" in self.model_name or "claude" in self.model_name or "gemini" in self.model_name:
            for prompt in full_prompts:
                prompt[0]['content']=prompt[0]['content']+break_task
        # else:
        #     for ind in range(len(full_prompts)):
        #         full_prompts[ind]=full_prompts[ind]+break_task
                
        
        if self.model_name=='vicuna':
            outputs_list = self.model.batched_generate(full_prompts, 
                                                            max_n_tokens = self.max_n_tokens,  
                                                            temperature = self.temperature,
                                                            top_p = self.top_p,
                                                            do_sample=False
                                                        )
        else:
            outputs_list = self.model.batched_generate(full_prompts, 
                                                            max_n_tokens = self.max_n_tokens,  
                                                            temperature = self.temperature,
                                                            top_p = self.top_p
                                                        )
        return outputs_list



def load_indiv_model(model_name, device=None):
    model_path, template = get_model_path_and_template(model_name)
    if model_name in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-2024-04-09", "gpt-4o-2024-05-13", "gpt-3.5-turbo-0125"]:
        lm = GPT(model_name)
    elif model_name in ["claude-2", "claude-instant-1", "claude-3-5-sonnet-20240620"]:
        lm = Claude(model_name)
    elif model_name in ["gemini-1.5-pro"]:
        lm = PaLM(model_name)
    elif model_name in ["finetuned-pythia"]:
        model = AutoModelForCausalLM.from_pretrained(
                "EleutherAI/pythia-1.4b",
                cache_dir=".cache",
                low_cpu_mem_usage=True,
                device_map="balanced")
        tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1.4b")
        current_dir = os.getcwd()
        checkpoint_dir = os.path.join(current_dir, "policy.pt")
        lm = FinetunedCheckpoint(model_name, model, tokenizer, checkpoint_dir)
    elif model_name in ["finetuned-vicuna"]:
        model = AutoModelForCausalLM.from_pretrained(
            "lmsys/vicuna-7b-v1.5",
            cache_dir=".cache",
            low_cpu_mem_usage=True,
            device_map="balanced"
        )
        tokenizer = AutoTokenizer.from_pretrained("lmsys/vicuna-7b-v1.5")
        checkpoint_dir = "/data/user_data/yifanwu6/yifanwu6/09022155test/checkpoints/policy.pt"
        lm = FinetunedCheckpoint(model_name, model, tokenizer, checkpoint_dir)

    
        
    else:
        model = AutoModelForCausalLM.from_pretrained(
                model_path, 
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,device_map="auto").eval()

        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            use_fast=False
        ) 

        if 'llama-2' in model_path.lower():
            tokenizer.pad_token = tokenizer.unk_token
            tokenizer.padding_side = 'left'
        if 'vicuna' in model_path.lower():
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = 'left'
        if not tokenizer.pad_token:
            tokenizer.pad_token = tokenizer.eos_token

        lm = HuggingFace(model_name, model, tokenizer)
    
    return lm, template

def get_model_path_and_template(model_name):
    full_model_dict={
        "gpt-4o-2024-05-13":{
            "path":"gpt-4",
            "template":"gpt-4"
        },
        "gpt-4-1106-preview":{
            "path":"gpt-4",
            "template":"gpt-4"
        },
        "gpt-3.5-turbo-0125": {
            "path":"gpt-3.5-turbo",
            "template":"gpt-3.5-turbo"
        },
        "vicuna":{
            "path":VICUNA_PATH,
            "template":"vicuna_v1.5"
        },
        "llama-2":{
            "path":LLAMA_PATH,
            "template":"llama-2"
        },
        "claude-instant-1":{
            "path":"claude-instant-1",
            "template":"claude-instant-1"
        },
        "claude-3-5-sonnet-20240620":{
            "path":"claude-2",
            "template":"claude-2"
        },
        "gemini-1.5-pro":{
            "path":"palm-2",
            "template":"palm-2"
        },
        "finetuned-pythia": {
            "path": "finetuned-pythia",
            "template": "vicuna_v1.5" #Using a template that is pre-included
        },
        "finetuned-vicuna": {
            "path": "finetuned-vicuna",
            "template": "vicuna_v1.5"
        }
    }
    path, template = full_model_dict[model_name]["path"], full_model_dict[model_name]["template"]
    return path, template



    
