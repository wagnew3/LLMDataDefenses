# Code for Data Defenses Agsinst LLMs Project

## Installation

1. git clone git@github.com:wagnew3/LLMDataDefenses.git
2. cd LLMDataDefenses/
3. conda env create -n ENVNAME --file ENV.yml
4. Follow step 2 of https://platform.openai.com/docs/quickstart?context=python to set up openai API key. If you do not have a key contact Willie (wagnew@andrew.cmu.edu) for one. Please note that openai API calls cost ~$0.001--don't make thousands of calls without consulting with Willie first.

## Code Overview
- src/test.py: scratch code for testing ways of triggering safety filters
- src/JailbreakingLLMs: clone of JailbreakingLLMs repo with a few bugs fixed. Modifying to fit our needs. run 
