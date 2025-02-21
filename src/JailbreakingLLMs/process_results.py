import pickle
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt;
import numpy as np;
import scipy.optimize as opt;
import conversers
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import scipy.stats as st 
import math
import random
import csv

def get_text_ratios_test():
    exp_results=[]
    results_dir="/home/willie/github/LLMDataDefenses/results/experiments/gpt4o"
    for file in os.listdir(results_dir):
        if file[-2:]=='.p':
            results_file=os.path.join(results_dir, file)
            
            try:
                exp_result=pickle.load(open(results_file, 'rb'))
                def_length=exp_result['args'].defense_length
                exp_results.append(exp_result)
            except:
                print('error', results_file)
    
    defense_method_results={}
    for exp_result in exp_results:
        defense_method=exp_result['args'].attack_type
        task=exp_result['args'].break_task
        model=exp_result['args'].target_model
        countermeasure=exp_result['args'].countermeasure[0]
        defense_length=exp_result['args'].dataset
        if not model in defense_method_results:
            defense_method_results[model]={}
        if defense_method not in defense_method_results[model]:
            defense_method_results[model][defense_method]={}
        if countermeasure not in defense_method_results[model][defense_method]:
            defense_method_results[model][defense_method][countermeasure]={}
        if defense_length not in defense_method_results[model][defense_method][countermeasure]:
            defense_method_results[model][defense_method][countermeasure][defense_length]={}
        defense_method_results[model][defense_method][countermeasure][defense_length][task]=exp_result#['judge_defense_score']
    
    # print(exp_results[2]['defense'][0])
    
    # Make defense to defended text length ratio tradeoff plot
    for model in defense_method_results:
        defense_methods=list(defense_method_results[model].keys())
        countermeasures=list(defense_method_results[model][defense_methods[0]].keys())
        defense_lengths=list(defense_method_results[model][defense_methods[0]][countermeasures[0]].keys())
        tasks=list(defense_method_results[model][defense_methods[0]][countermeasures[0]][defense_lengths[0]].keys())
        
        colors=['b', 'g', 'r', 'c', 'm', 'y']
        fig, ax = plt.subplots(figsize=(6,4))
        #ax = plt.subplot(111)
        text_ratios=[]
        defense_success=[]
        a=len(defense_methods)
        for model in defense_method_results.keys():
            for defense_method in defense_method_results[model].keys():
                #defense_method=defense_methods[defense_method_ind]
                if defense_method=='generate_jailbreaks':
                    defense_results=[]
                    
                    for countermeasure in defense_method_results[model][defense_method].keys():
                        countermeasure_perf=0
                        num_countermeasure_tests=0
                        for defense_length in defense_method_results[model][defense_method][countermeasure].keys():
                            for task in defense_method_results[model][defense_method][countermeasure][defense_length].keys():
                                # try:
                                task_scores=defense_method_results[model][defense_method][countermeasure][defense_length][task]['judge_defense_score']
                                # except:
                                #     print('error!', model, defense_method, countermeasure, task)
                                #     continue
                                for task_score_ind in range(len(task_scores)):
                                    defense_success.append(task_scores[task_score_ind][-1]>=7)
                                    if task==None: #RAG
                                        protection_length=len(defense_method_results[model][defense_method][countermeasure][defense_length][task]['defense'][task_score_ind][-1])
                                        undefended_length=len(defense_method_results[model][defense_method][countermeasure][defense_length][task]['undefended_text'][task_score_ind][0])
                                    else:
                                        protection_length=len(defense_method_results[model][defense_method][countermeasure][defense_length][task]['defense'][task_score_ind][-1])
                                        undefended_length=len(defense_method_results[model][defense_method][countermeasure][defense_length][task]['undefended_text'][task_score_ind])
                                    
                                    if protection_length/undefended_length>1:
                                        u=0
                                    
                                    text_ratios.append(undefended_length/protection_length)
                                # except:
                                #     print('error!', model, defense_method, countermeasure, task)
                            
        # a, b = np.polyfit(text_ratios, defense_success, 1)
        # fit_equation = lambda x: a * x + b 
        # X_fit = np.linspace(min(text_ratios), max(text_ratios), 1000)
        # Y_fit = fit_equation(X_fit)
        # plt.plot(X_fit, Y_fit, color='r', alpha=0.5, label='Linear Fit')
    
        # Generate some data, you don't have to do this, as you already have your data
        text_ratios=np.array(text_ratios)
        mean_ratio=np.mean(text_ratios)
        defense_success=np.array(defense_success).astype(np.int32)
        # Plot the actual data
        bins = np.linspace(0, np.max(text_ratios), 10)
        bin_means = (np.histogram(text_ratios, bins, weights=defense_success)[0] /np.histogram(text_ratios, bins)[0])
        bin_labels=np.digitize(text_ratios, bins[1:])
        bin_cis=[]
        for ind in range(len(bin_means)):
            bin_vals=np.extract(bin_labels==ind, defense_success)
            ci=st.t.interval(0.95, df=len(bin_vals)-1, 
                      loc=np.mean(bin_vals), 
                      scale=st.sem(bin_vals))
            bin_cis.append((ci[1]-ci[0])/2.0)

        plt.bar(bins[:-1]+(bins[1]-bins[0])/2, bin_means, width=bins[1]-bins[0], color='b', edgecolor='k',linewidth=1, yerr=bin_cis)
        #plt.plot(text_ratios, defense_success, ".", label="Data");
    
        # The actual curve fitting happens here
        # optimizedParameters, pcov = opt.curve_fit(func, text_ratios, defense_success);
    
        # Use the optimized parameters to plot the best fit
        # plt.plot(text_ratios, func(text_ratios, *optimizedParameters), label="fit");
        plt.xlabel("Ratio of Defended Text Length to Defense Length")
        plt.ylabel("Defense Success Rate")
        
        #ax.set_xscale('log')
        # Show the graph
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'/home/willie/github/LLMDataDefenses/results/experiments/defense_text_ratio.png')
        plt.show()
    return text_ratios, defense_success

def load_results(results_dir, dataset=None):
    exp_results=[]
    for file in os.listdir(results_dir):
        if file[-2:]=='.p':
            results_file=os.path.join(results_dir, file)
            exp_result=pickle.load(open(results_file, 'rb'))
            if isinstance(exp_result, dict):
                def_length=exp_result['args'].defense_length
                exp_results.append(exp_result)
    
    defense_method_results={}
    for exp_result in exp_results:
        defense_method=exp_result['args'].attack_type
        task=exp_result['args'].break_task
        model=exp_result['args'].target_model
        exp_dataset=exp_result['args'].dataset
        if dataset is None or exp_dataset==dataset:
            countermeasure=exp_result['args'].countermeasure[0]
            if not model in defense_method_results:
                defense_method_results[model]={}
            if defense_method not in defense_method_results[model]:
                defense_method_results[model][defense_method]={}
            if countermeasure not in defense_method_results[model][defense_method]:
                defense_method_results[model][defense_method][countermeasure]={}
            defense_method_results[model][defense_method][countermeasure][task]=exp_result
            
    return defense_method_results

def graph_transfer_results(other_results_dirs, save_loc):
    defense_method_results={}
    for other_results_dir in other_results_dirs:
        other_defense_method_results=load_results(other_results_dir)
        transfer_name=other_results_dir.split('/')[-1]
        defense_method_results[transfer_name]=other_defense_method_results[list(other_defense_method_results.keys())[0]]
        # defense_method_results.update(other_defense_method_results)
    
    colors=['b', 'grey', 'r', 'c', 'm', 'y']
    fig, ax = plt.subplots(figsize=(5,2.5))
    width=0.8
    all_defense_results=[]
    all_defense_methods_countermeasures=[]
    
    models=['gpt4o to gpt4o\n unseen text', 'meta-llama-3.1-8B-instruct\n to gpt4o unseen text']
    defense_results=[]
    defense_ci=[]
    x=np.array([i for i in range(2)])
    for model in defense_method_results:
        #models.append(model)
        countermeasure_perf=0
        num_countermeasure_tests=0
        defense_methods=list(defense_method_results[model].keys())
        if 'generate_jailbreaks' in defense_methods:
            if 'substitute' in defense_methods:
                defense_methods.remove('substitute')
            if 'jailbreaks' in defense_methods:
                defense_methods.remove('jailbreaks')
        defense_methods.sort()
        countermeasures=list(defense_method_results[model][defense_methods[0]].keys())
        countermeasures.sort()
        tasks=list(defense_method_results[model][defense_methods[0]][countermeasures[0]].keys())
        
    
        
        for defense_method_ind in range(len(defense_methods)):
            defense_method=defense_methods[defense_method_ind]
            
    
            for countermeasure in countermeasures:
                
                countermeasure_results=[]
                for task in tasks:
                    try:
                        task_scores=defense_method_results[model][defense_method][countermeasure][task]['judge_defense_score']
                    except:
                        #print('error!', model, defense_method, countermeasure, task)
                        continue
                    # if len(task_scores)!=50:
                    #     print(model, defense_method, countermeasure, task)
                    ind=0
                    for task_score in task_scores:
                        if len(task_score)>0:
                            countermeasure_perf+=task_score[-1]>=7
                            countermeasure_results.append(task_score[-1]>=7)
                            if task_score[-1]>=7:
                                print('`'+defense_method_results[model][defense_method][countermeasure][task]['defense'][ind][-1].replace("\\", "\\\\").replace("`", "\`")+'`'+",")
                        num_countermeasure_tests+=1
                        ind+=1
                # if (dataset=='RAG' and num_countermeasure_tests<75) or (dataset!='RAG' and num_countermeasure_tests<25):
                #     print(model, defense_method, countermeasure, task)
        if num_countermeasure_tests>0:
            countermeasure_perf=countermeasure_perf/num_countermeasure_tests
        else:
            countermeasure_perf=0
        defense_results.append(countermeasure_perf)
        ci=st.t.interval(0.95, df=len(countermeasure_results)-1, 
          loc=np.mean(countermeasure_results), 
          scale=st.sem(countermeasure_results))
        if math.isnan(ci[1]):
            defense_ci.append(0)
        else:
            defense_ci.append((ci[1]-ci[0])/2.0)
                        
    # models[models.index('vicuna')]='meta-llama-3.1-8B-instruct'               
                    
    ax.bar(x, defense_results, yerr=defense_ci, width=width, color=colors, align='center')
            # except:
            #     print('error!')
    
        

        
        
        # tukey = pairwise_tukeyhsd(endog=all_defense_results,     # Data
        #                           groups=all_defense_methods_countermeasures,   # Groups
        #                           alpha=0.05)          # Significance level
        #
        # tukey.plot_simultaneous() 
    
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=0)
    
    ax.set_xlabel("Countermeasure Type")
    ax.set_ylabel("Attack Failure Rate")
    ax.set_title(f'Defense Transfer to Unseen Models and Texts')
    ax.set_ylim([0, 1])
    plt.xlim([0-0.4,2-1+0.4])
    #ax.autoscale(tight=True)
    plt.tight_layout()
    #ax.legend(loc='lower right', bbox_to_anchor=(1, -0.65))
    plt.savefig(f'../../results/transfer_results.png')
    #plt.show()

    u=0

def graph_other_models_results(other_results_dirs, save_loc):
    defense_method_results={}
    for other_results_dir in other_results_dirs:
        other_defense_method_results=load_results(other_results_dir, dataset='llmprivacy')
        defense_method_results.update(other_defense_method_results)
    
    colors=['b', 'grey', 'r', 'c', 'm', 'y']
    fig, ax = plt.subplots(figsize=(6,4))
    width=0.8
    all_defense_results=[]
    all_defense_methods_countermeasures=[]
    
    models=[]
    defense_results=[]
    defense_ci=[]
    x=np.array([i for i in range(4)])
    for model in defense_method_results:
        models.append(model)
        countermeasure_perf=0
        num_countermeasure_tests=0
        defense_methods=list(defense_method_results[model].keys())
        if 'generate_jailbreaks' in defense_methods:
            if 'substitute' in defense_methods:
                defense_methods.remove('substitute')
            if 'jailbreaks' in defense_methods:
                defense_methods.remove('jailbreaks')
            if 'nothing' in defense_methods:
                defense_methods.remove('nothing')
        defense_methods.sort()
        countermeasures=['']#list(defense_method_results[model][defense_methods[0]].keys())
        countermeasures.sort()
        tasks=list(defense_method_results[model][defense_methods[0]][countermeasures[0]].keys())
        
    
        
        for defense_method_ind in range(len(defense_methods)):
            defense_method=defense_methods[defense_method_ind]
            
    
            for countermeasure in countermeasures:
                
                countermeasure_results=[]
                for task in tasks:
                    try:
                        task_scores=defense_method_results[model][defense_method][countermeasure][task]['judge_defense_score']
                    except:
                        print('error!', model, defense_method, countermeasure, task)
                        continue
                    # if len(task_scores)!=50:
                    #     print(model, defense_method, countermeasure, task)
                    for task_score in task_scores:
                        if len(task_score)>0:
                            countermeasure_perf+=task_score[-1]>=7
                            countermeasure_results.append(task_score[-1]>=7)
                        num_countermeasure_tests+=1
                # if (dataset=='RAG' and num_countermeasure_tests<75) or (dataset!='RAG' and num_countermeasure_tests<25):
                #     print(model, defense_method, countermeasure, task)
        if num_countermeasure_tests>0:
            countermeasure_perf=countermeasure_perf/num_countermeasure_tests
        else:
            countermeasure_perf=0
        defense_results.append(countermeasure_perf)
        ci=st.t.interval(0.95, df=len(countermeasure_results)-1, 
          loc=np.mean(countermeasure_results), 
          scale=st.sem(countermeasure_results))
        if math.isnan(ci[1]):
            defense_ci.append(0)
        else:
            defense_ci.append((ci[1]-ci[0])/2.0)
                        
    models[models.index('vicuna')]='meta-llama-3.1-8B-instruct'               
                    
    ax.bar(x, defense_results, yerr=defense_ci, width=width, color=colors, align='center')
            # except:
            #     print('error!')
    
        

        
        
        # tukey = pairwise_tukeyhsd(endog=all_defense_results,     # Data
        #                           groups=all_defense_methods_countermeasures,   # Groups
        #                           alpha=0.05)          # Significance level
        #
        # tukey.plot_simultaneous() 
    
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45)
    
    ax.set_xlabel("Countermeasure Type")
    ax.set_ylabel("Attack Failure Rate")
    ax.set_title(f'Defense Performance on Other Leading Models')
    ax.set_ylim([0, 1])
    plt.xlim([0-0.4,4-1+0.4])
    #ax.autoscale(tight=True)
    plt.tight_layout()
    ax.legend(loc='lower right', bbox_to_anchor=(1, -0.65))
    plt.savefig(f'../../results/other_models_results.png')
    #plt.show()

    u=0

model_map={"gpt-4o-2024-05-13": "gpt-4o-2024-05-13", "gemini-1.5-pro":"gemini-1.5-pro", "claude-3-5-sonnet-20240620":"claude-3-5-sonnet-20240620", "vicuna": "meta-llama-3.1-8B-instruct"}
countermeasure_name_map={'smoothllm':'smoothllm', 'ppl-5-3.5':'ppl-5-3.5', 'proactive':'proactive', 'llm-based':'llm-based','sandwich':'sandwich', 'random_seq':'random_seq', 'delimiters':'delimiters', 'xml':'xml', 'paraphrasing':'paraphrasing', 'retokenization':'retokenization', '': 'no countermeasure', 'nothing': 'no countermeasure', 'prompt_guard': 'prompt guard'}
defense_name_map={'generate_jailbreaks': 'data defense (ours)', 'substitute': 'substitute (ours)', 'nothing': 'no data defense', 'jailbreaks': 'false answer unseen (ours)'}
if __name__ == '__main__':
    exp_result=pickle.load(open("/home/willie/github/LLMDataDefenses/results/experiments/focus+substitute_gpt-4o-mini_None_RAG_1_['focus+substitute']_729_1.p", 'rb'))
    #graph_transfer_results(["../../results/experiments/gpt4o"], "../../results")
    # exit()
    # graph_other_models_results(["../../results/experiments/gpt4o", "../../results/experiments/claude", "../../results/experiments/gemini", "../../results/experiments/llama-3.1-8b/experiments"], "../../results")
    # exit()
    #ext_ratios, defense_success=get_text_ratios_test()
    # load run results
    print(exp_result[10]['defense'][0][0][0][0])
    print(exp_result[10]['defense'][0][0][0][1])
    
    mean_scores=[]
    for result in exp_result:
        total=0
        for res in result['judge_defense_score']:
            total+=res[0][0]
        mean_scores.append(total/len(result['judge_defense_score']))
    
    undefended_responses=[]
    defended_responses=[]
    all_scores=[]
    
    for dataset in ['wikibios', 'llmprivacy', 'RAG']:
        
        for dir in os.listdir("/home/willie/github/LLMDataDefenses/results/experiments"):
            results_dir="/home/willie/github/LLMDataDefenses/results/experiments/gpt4_dialogue_attack"#os.path.join("/home/willie/github/LLMDataDefenses/results/experiments", dir)
            if os.path.exists(os.path.join(results_dir, 'experiments')):
                results_dir=os.path.join(results_dir, 'experiments')
            if os.path.isdir(results_dir):
                defense_method_results=load_results(results_dir, dataset=dataset)
                continue
                #Make bar charts
                u=0
                for model in defense_method_results:
                    defense_methods=list(defense_method_results[model].keys())
                    if 'generate_jailbreaks' in defense_methods:
                        if 'substitute' in defense_methods:
                            defense_methods.remove('substitute')
                        if 'jailbreaks' in defense_methods:
                            defense_methods.remove('jailbreaks')
                    defense_methods.sort()
                    countermeasures=list(defense_method_results[model][defense_methods[0]].keys())
                    countermeasures.sort()
                    tasks=list(defense_method_results[model][defense_methods[0]][countermeasures[0]].keys())
                    x=np.array([i for i in range(len(countermeasures))])
                
                    colors=['b', 'grey', 'r', 'c', 'm', 'y']
                    fig, ax = plt.subplots(figsize=(12,3))
                    width=0.8/len(defense_methods)
                    all_defense_results=[]
                    all_defense_methods_countermeasures=[]
                    for defense_method_ind in range(len(defense_methods)):
                        defense_method=defense_methods[defense_method_ind]
                        defense_results=[]
                        defense_ci=[]
                
                        for countermeasure in countermeasures:
                            countermeasure_perf=0
                            num_countermeasure_tests=0
                            countermeasure_results=[]
                            for task in tasks:
                                try:
                                    task_scores=defense_method_results[model][defense_method][countermeasure][task]['judge_defense_score']
                                except:
                                    print('error!', model, defense_method, countermeasure, task)
                                    continue
                                # if len(task_scores)!=50:
                                #     print(model, defense_method, countermeasure, task)
                                
                                for ind in range(len(defense_method_results[model][defense_method][countermeasure][task]['undefended_response'])):
                                    if defense_method_results[model][defense_method][countermeasure][task]['undefended_response'][ind][-1][0]=="":
                                        u=0
                                    undefended_responses.append(defense_method_results[model][defense_method][countermeasure][task]['undefended_response'][ind][-1])
                                    defended_responses.append(defense_method_results[model][defense_method][countermeasure][task]['defended response'][ind][-1])
                                    all_scores.append(defense_method_results[model][defense_method][countermeasure][task]['judge_defense_score'][ind][-1])
                                
                                for task_score in task_scores:
                                    if len(task_score)>0:
                                        countermeasure_perf+=task_score[-1]>=7
                                        countermeasure_results.append(task_score[-1]>=7)
                                    num_countermeasure_tests+=1
                            if (dataset=='RAG' and num_countermeasure_tests<75) or (dataset!='RAG' and num_countermeasure_tests<25):
                                print(model, defense_method, countermeasure, task)
                            if num_countermeasure_tests>0:
                                countermeasure_perf=countermeasure_perf/num_countermeasure_tests
                            else:
                                countermeasure_perf=0
                            defense_results.append(countermeasure_perf)
                            ci=st.t.interval(0.95, df=len(countermeasure_results)-1, 
                              loc=np.mean(countermeasure_results), 
                              scale=st.sem(countermeasure_results))
                            if math.isnan(ci[1]):
                                defense_ci.append(0)
                            else:
                                defense_ci.append((ci[1]-ci[0])/2.0)
                                    
                                
                                
                        ax.bar(x-0.2+width*defense_method_ind, defense_results, yerr=defense_ci, width=width, color=colors[defense_method_ind], align='center', label=defense_name_map[defense_method])
                        # except:
                        #     print('error!')
                
                    
        
                    
                    
                    # tukey = pairwise_tukeyhsd(endog=all_defense_results,     # Data
                    #                           groups=all_defense_methods_countermeasures,   # Groups
                    #                           alpha=0.05)          # Significance level
                    #
                    # tukey.plot_simultaneous() 
                
                    ax.set_xticks(x)
                    ax.set_xticklabels([countermeasure_name_map[countermeasure] for countermeasure in countermeasures], rotation=45)
                    
                    ax.set_xlabel("Countermeasure Type")
                    ax.set_ylabel("Attack Failure Rate")
                    ax.set_title(f'{model_map[model]} on {dataset}')
                    ax.set_ylim([0, 1])
                    plt.xlim([0-0.4,len(countermeasures)-1+0.4])
                    #ax.autoscale(tight=True)
                    plt.tight_layout()
                    ax.legend(loc='lower right', bbox_to_anchor=(1, -1.25))
                    plt.savefig(f'{results_dir}/{dataset}_{model}_full_results.png')
                    #plt.show()
                
                    u=0
        
        # Make text ratios plots
        # text_ratios, defense_success=get_text_ratios_test()
        #
        # gen_text_ratios=[]
        # gen_defense_success=[]
        # for model in defense_method_results:
        #     defense_methods=list(defense_method_results[model].keys())
        #     countermeasures=list(defense_method_results[model][defense_methods[0]].keys())
        #     tasks=list(defense_method_results[model][defense_methods[0]][countermeasures[0]].keys())
        #     x=np.array([i for i in range(len(countermeasures))])
        #
        #     colors=['b', 'g', 'r', 'c', 'm', 'y']
        #     ax = plt.subplot(111)
        #     width=0.8/len(defense_methods)
        #     for defense_method_ind in range(len(defense_methods)):
        #         defense_method=defense_methods[defense_method_ind]
        #         if defense_method=='generate_jailbreaks':
        #             defense_results=[]
        #
        #             for countermeasure in countermeasures:
        #                 countermeasure_perf=0
        #                 num_countermeasure_tests=0
        #                 for task in tasks:
        #                     task_scores=defense_method_results[model][defense_method][countermeasure][task]
        #                     for task_score in task_scores:
        #                         countermeasure_perf+=task_score[-1]>=7
        #                         num_countermeasure_tests+=1
        #                 countermeasure_perf=countermeasure_perf/num_countermeasure_tests
        #                 defense_results.append(countermeasure_perf)
        #
        #         # This is the function we are trying to fit to the data.
        #     a, b = np.polyfit(text_ratios, defense_success, 1)
        #     fit_equation = lambda x: a * x + b 
        #     X_fit = np.linspace(min(text_ratios), max(text_ratios), 1000)
        #     Y_fit = fit_equation(X_fit)
        #     plt.plot(X_fit, Y_fit, color='r', alpha=0.5, label='Linear Fit')
        #
        #     # Generate some data, you don't have to do this, as you already have your data
        #     text_ratios=np.array(text_ratios)
        #     defense_success=np.array(defense_success)
        #     # Plot the actual data
        #     plt.plot(text_ratios, defense_success, ".", label="Data");
        #
        #     # The actual curve fitting happens here
        #     # optimizedParameters, pcov = opt.curve_fit(func, text_ratios, defense_success);
        #
        #     # Use the optimized parameters to plot the best fit
        #     # plt.plot(text_ratios, func(text_ratios, *optimizedParameters), label="fit");
        #     plt.xlabel("Ratio of Defense Length to Text Length")
        #     plt.ylabel("Defense Success Rate")
        #     # Show the graph
        #     plt.legend()
        #     plt.show()
    u=0
    
    c = list(zip(undefended_responses, defended_responses, all_scores))
    random.shuffle(c)
    undefended_responses, defended_responses, all_scores = zip(*c)
    
    with open("/home/willie/github/LLMDataDefenses/results/judge_validation.csv", 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for ind in range(100):
            wr.writerow([undefended_responses[ind], defended_responses[ind], all_scores[ind]])
        
            