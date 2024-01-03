import pickle
import os
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    # load run results
    exp_results=[]
    results_dir='../results/experiments'
    for file in os.listdir(results_dir):
        if file[-2:]=='.p':
            results_file=os.path.join(results_dir, file)
            exp_result=pickle.load(open(results_file, 'rb'))
            exp_results.append(exp_result)
    
    defense_method_results={}
    for exp_result in exp_results:
        defense_method=exp_result['args'].attack_type
        attacker_model=exp_result['args'].target_model
        task=exp_result['args'].break_task
        if attacker_model=='vicuna':
            if defense_method not in defense_method_results:
                defense_method_results[defense_method]={}
            defense_method_results[defense_method][task]=exp_result['judge_defense_score']
        
    print(exp_results[2]['defense'][0])
    
    defense_methods=list(defense_method_results.keys())
    tasks=list(defense_method_results[defense_methods[0]].keys())
    x=np.array([i for i in range(len(tasks))])
    
    colors=['b', 'g', 'r', 'c', 'm', 'y']
    ax = plt.subplot(111)
    width=0.8/len(defense_methods)
    for defense_method_ind in range(len(defense_methods)):
        defense_method=defense_methods[defense_method_ind]
        defense_results=[]
        for task in tasks:
            defense_results.append(np.mean(np.array(defense_method_results[defense_method][task])))
        ax.bar(x-0.3+width*defense_method_ind, defense_results, width=width, color=colors[defense_method_ind], align='center', label=defense_method)
    
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation='vertical')
    ax.legend()
    #ax.autoscale(tight=True)
    plt.show()
    
    u=0