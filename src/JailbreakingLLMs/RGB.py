# https://github.com/chen700564/RGB

import json
import numpy as np
import random, math
import argparse,torch
import os
import json, tqdm, requests
import yaml
    
def processdata(instance, noise_rate, passage_num, filename, correct_rate = 0):
    query = instance['query']
    ans = instance['answer']

    neg_num = math.ceil(passage_num * noise_rate)
    pos_num = passage_num - neg_num

    if '_int' in filename:
        for i in instance['positive']:
            random.shuffle(i)
        print(len(instance['positive']))
        docs = [i[0] for i in instance['positive']]
        if len(docs) < pos_num:
            maxnum = max([len(i) for i in instance['positive']])
            for i in range(1,maxnum):
                for j in instance['positive']:
                    if len(j) > i:
                        docs.append(j[i])
                        if len(docs) == pos_num:
                            break
                if len(docs) == pos_num:
                    break
        neg_num = passage_num - len(docs)
        if neg_num > 0:
            negative = instance['negative'][:neg_num]
            docs += negative
    elif '_fact' in filename:
        correct_num = math.ceil(passage_num * correct_rate)
        pos_num = passage_num - neg_num - correct_num
        indexs = list(range(len(instance['positive'])))
        selected = random.sample(indexs,min(len(indexs),pos_num))
        docs = [instance['positive_wrong'][i] for i in selected]
        remain = [i for i in indexs if i not in selected]
        if correct_num > 0 and len(remain) > 0:
            docs += [instance['positive'][i] for i in random.sample(remain,min(len(remain),correct_num))]
        if neg_num > 0:
            docs += instance['negative'][:neg_num]
    else:
        if noise_rate == 1:
            neg_num = passage_num
            pos_num = 0
        else:
            if neg_num > len(instance['negative']):
                neg_num = len(instance['negative'])
                pos_num = passage_num - neg_num
            elif pos_num > len(instance['positive']):
                pos_num = len(instance['positive'])
                neg_num = passage_num - pos_num
        

        positive = instance['positive'][:pos_num]
        negative = instance['negative'][:neg_num]

        docs = positive + negative

    random.shuffle(docs)
    
    return query, ans, docs


def checkanswer(prediction, ground_truth):
    prediction = prediction.lower()
    if type(ground_truth) is not list:
        ground_truth = [ground_truth]
    labels = []
    for instance in ground_truth:
        flag = True
        if type(instance)  == list:
            flag = False 
            instance = [i.lower() for i in instance]
            for i in instance:
                if i in prediction:
                    flag = True
                    break
        else:
            instance = instance.lower()
            if instance not in prediction:
                flag = False
        labels.append(int(flag))
    return labels

def getevalue(results):
    results = np.array(results)
    results = np.max(results,axis = 0)
    if 0 in results:
        return False
    else:
        return True
            

def predict(query, ground_truth, docs, model, system, instruction, temperature, dataset):

    '''
    label: 0 for positive, 1 for negative, -1 for not enough information

    '''
    if len(docs) == 0:

        text = instruction.format(QUERY=query, DOCS='')
        prediction = model.generate(text, temperature)

    else:

        docs = '\n'.join(docs)

        

        text = instruction.format(QUERY=query, DOCS=docs)

        prediction = model.generate(text, temperature, system)

    if 'zh' in dataset:
        prediction = prediction.replace(" ","")

    if '信息不足' in prediction or 'insufficient information' in prediction:
        labels = [-1]
    else:
        labels = checkanswer(prediction, ground_truth)
    
    factlabel = 0

    if '事实性错误' in prediction or 'factual errors' in prediction:
        factlabel = 1

    return labels,prediction, factlabel

class RAG_Getter():
    
    def __init__(self, shuffle_seed=0):
        self.noise_rate = 0.0
        self.passage_num = 1
        self.dataset='en'
        self.correct_rate=0
    
        instances = []
        with open(f'RGB/data/en.json','r') as f:
            for line in f:
                instances.append(json.loads(line))
        if 'en' in self.dataset:
            resultpath = 'result-en'
        elif 'zh' in self.dataset:
            resultpath = 'result-zh'
    
        if False:
            prompt = yaml.load(open('config/instruction_fact.yaml', 'r'), Loader=yaml.FullLoader)[self.dataset[:2]]
            resultpath = resultpath + '/fact'
        else:
            prompt = yaml.load(open('RGB/config/instruction.yaml', 'r'), Loader=yaml.FullLoader)[self.dataset[:2]]
    
        self.system = prompt['system']
        self.instruction = prompt['instruction']
      
        random.seed(shuffle_seed)
        random.shuffle(instances)
        self.instances=instances
        
    def get_query_instance(self, query_number):
        instance=self.instances[query_number]
        query, ans, docs = processdata(instance, self.noise_rate, self.passage_num, self.dataset, self.correct_rate)
        

        return query, ans, docs
    
    def make_query(self, query, ans, docs):
        user_text=self.instruction.format(QUERY=query, DOCS=docs)
        return self.system, user_text
    
    
