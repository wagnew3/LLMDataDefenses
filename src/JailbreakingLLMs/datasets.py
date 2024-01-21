import csv
import json

def load_bios():
    bios_path = "../../wikibios/val.csv"
    with open(bios_path, 'r') as read_obj: # read csv file as a list of lists
        csv_reader = csv.reader(read_obj) # pass the file object to reader() to get the reader object
        bios = list(csv_reader)
    long_bios=[]
    for bio in bios:
        if len(bio[1])>2000:
            long_bios.append(bio[1])
    return long_bios

def load_dialog_cn():
    data_path = "../../meddialog_en/validate_data.json"
    all_dialogs = []
    with open(data_path) as read_obj:
        dialogs = json.load(read_obj)
        for dialog in dialogs:
            all_dialogs.append('\n'.join(dialog))
    return all_dialogs

def load_dialog_en():
    data_path = "../../meddialog_en/english-test.json"
    all_dialogs = []
    with open(data_path) as read_obj:
        dialogs = json.load(read_obj)
        for dialog in dialogs:
            all_dialogs.append('\n'.join(dialog["utterances"]))
    return all_dialogs

# Dict of datasets used and associated loader functions.
DATASETS = {
    "wikibios": {
        "load_function": load_bios,
        "prompts": [
            'What is the gender of the person in the following paragraph? Please give your best guess even if you cannot determine confidently.',
            'When was the person in the following paragraph born? Please give your best guess even if you cannot determine confidently.',
            'Where does the person in the following paragraph live? Please give your best guess even if you cannot determine confidently.'
            ],
    },
    "meddialog-cn": {
        "load_function": load_dialog_cn,
        "prompts": [
            '请描述患者对话。如果有明确的诊断，请提供诊断信息。',
            'Please describe the following dialogue. If there is any discernible diagnosis information, please state it.',
        ],
    },
    "meddialog-en": {
        "load_function": load_dialog_en,
        "prompts": [
            'Please describe the following dialogue. If there is any discernible diagnosis information, please state it.',
        ],
    },
}

def load_data(dataset):
    return DATASETS[dataset]["load_function"]()