for target_model in gpt-4o-2024-05-13
do
	for break_task_ind in 0 1 2
	do
		for defense_type in substitute generate_jailbreaks obscene_reddits bio_sentance nothing
		do
			for countermeasure in None ppl-5-3.5 proactive llm-based sandwich random_seq delimiters xml paraphrasing retokenization smoothllm
			do
				python main.py --target-model $target_model --break_task_ind $break_task_ind --attack_type $defense_type --countermeasure $countermeasure
				exit 0

			done
		done
	
	done



echo $i
done