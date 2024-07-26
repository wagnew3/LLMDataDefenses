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

def get_text_ratios_test():
    exp_results=[]
    results_dir="/home/willie/github/LLMDataDefenses/results/experiments/full_exps/gpt4o"
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
        defense_length=exp_result['args'].defense_length
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
        ax = plt.subplot(111)
        text_ratios=[]
        defense_success=[]
        a=len(defense_methods)
        for defense_method_ind in range(len(defense_methods)):
            defense_method=defense_methods[defense_method_ind]
            if defense_method=='generate_jailbreaks':
                defense_results=[]
                
                for countermeasure in countermeasures:
                    countermeasure_perf=0
                    num_countermeasure_tests=0
                    for defense_length in defense_lengths:
                        for task in tasks:
                            try:
                                task_scores=defense_method_results[model][defense_method][countermeasure][defense_length][task]['judge_defense_score']
                            except:
                                print('error!', model, defense_method, countermeasure, task)
                                continue
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
                                
                                text_ratios.append(protection_length/undefended_length)
                            # except:
                            #     print('error!', model, defense_method, countermeasure, task)
                        
        a, b = np.polyfit(text_ratios, defense_success, 1)
        fit_equation = lambda x: a * x + b 
        X_fit = np.linspace(min(text_ratios), max(text_ratios), 1000)
        Y_fit = fit_equation(X_fit)
        plt.plot(X_fit, Y_fit, color='r', alpha=0.5, label='Linear Fit')
    
        # Generate some data, you don't have to do this, as you already have your data
        text_ratios=np.array(text_ratios)
        mean_ratio=np.mean(text_ratios)
        defense_success=np.array(defense_success)
        # Plot the actual data
        plt.plot(text_ratios, defense_success, ".", label="Data");
    
        # The actual curve fitting happens here
        # optimizedParameters, pcov = opt.curve_fit(func, text_ratios, defense_success);
    
        # Use the optimized parameters to plot the best fit
        # plt.plot(text_ratios, func(text_ratios, *optimizedParameters), label="fit");
        plt.xlabel("Ratio of Defense Length to Text Length")
        plt.ylabel("Defense Success Rate")
        
        ax.set_xscale('log')
        # Show the graph
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'/home/willie/github/LLMDataDefenses/results/experiments/defense_text_ratio.png')
        plt.show()
    return text_ratios, defense_success

countermeasure_name_map={'smoothllm':'smoothllm', 'ppl-5-3.5':'ppl-5-3.5', 'proactive':'proactive', 'llm-based':'llm-based','sandwich':'sandwich', 'random_seq':'random_seq', 'delimiters':'delimiters', 'xml':'xml', 'paraphrasing':'paraphrasing', 'retokenization':'retokenization', '': 'no countermeasure'}
defense_name_map={'generate_jailbreaks': 'false answer (ours)', 'substitute': 'substitute (ours)', 'nothing': 'no protection'}
if __name__ == '__main__':
    #text_ratios, defense_success=get_text_ratios_test()
    # load run results
    for dataset in ['wikibios', 'llmprivacy', 'RAG']:
        exp_results=[]
        results_dir="/home/willie/github/LLMDataDefenses/results/experiments/full_exps/claude"
        for file in os.listdir(results_dir):
            if file[-2:]=='.p':
                results_file=os.path.join(results_dir, file)
                exp_result=pickle.load(open(results_file, 'rb'))
                try:
                    def_length=exp_result['args'].defense_length
                    exp_results.append(exp_result)
                except:
                    u=0
        
        defense_method_results={}
        for exp_result in exp_results:
            defense_method=exp_result['args'].attack_type
            task=exp_result['args'].break_task
            model=exp_result['args'].target_model
            exp_dataset=exp_result['args'].dataset
            if exp_dataset==dataset:
                countermeasure=exp_result['args'].countermeasure[0]
                if not model in defense_method_results:
                    defense_method_results[model]={}
                if defense_method not in defense_method_results[model]:
                    defense_method_results[model][defense_method]={}
                if countermeasure not in defense_method_results[model][defense_method]:
                    defense_method_results[model][defense_method][countermeasure]={}
                defense_method_results[model][defense_method][countermeasure][task]=exp_result#['judge_defense_score']
        #Make bar charts
        for model in defense_method_results:
            defense_methods=list(defense_method_results[model].keys())
            defense_methods.sort()
            countermeasures=list(defense_method_results[model][defense_methods[0]].keys())
            countermeasures.sort()
            tasks=list(defense_method_results[model][defense_methods[0]][countermeasures[0]].keys())
            x=np.array([i for i in range(len(countermeasures))])
        
            colors=['b', 'g', 'r', 'c', 'm', 'y']
            fig, ax = plt.subplots(figsize=(12,5))
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
                        if len(task_scores)!=50:
                            print(model, defense_method, countermeasure, task)
                        for task_score in task_scores:
                            if len(task_score)>0:
                                countermeasure_perf+=task_score[-1]>=7
                                countermeasure_results.append(task_score[-1]>=7)
                            num_countermeasure_tests+=1
                    countermeasure_perf=countermeasure_perf/num_countermeasure_tests
                    defense_results.append(countermeasure_perf)
                    ci=st.t.interval(0.95, df=len(countermeasure_results)-1, 
                      loc=np.mean(countermeasure_results), 
                      scale=st.sem(countermeasure_results))
                    if math.isnan(ci[1]):
                        defense_ci.append(0)
                    else:
                        defense_ci.append((ci[1]-ci[0])/2.0)
                        
                    
                    
                ax.bar(x-0.3+width*defense_method_ind, defense_results, yerr=defense_ci, width=width, color=colors[defense_method_ind], align='center', label=defense_name_map[defense_method])
        
        
            

            
            
            # tukey = pairwise_tukeyhsd(endog=all_defense_results,     # Data
            #                           groups=all_defense_methods_countermeasures,   # Groups
            #                           alpha=0.05)          # Significance level
            #
            # tukey.plot_simultaneous() 
        
            ax.set_xticks(x)
            ax.set_xticklabels([countermeasure_name_map[countermeasure] for countermeasure in countermeasures], rotation=45)
            ax.legend()
            ax.set_xlabel("Countermeasure Type")
            ax.set_ylabel("Defense Success Rate")
            ax.set_title(dataset)
            ax.set_ylim([0, 1])
            #ax.autoscale(tight=True)
            plt.tight_layout()
            plt.savefig(f'/home/willie/github/LLMDataDefenses/results/experiments/{dataset}_full_results.png')
            plt.show()
        
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
            