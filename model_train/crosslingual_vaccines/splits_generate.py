
import csv
import json
import random
from collections import Counter
random.seed(2023)

def save_json(datasets, names, out_path):
    for i, split in enumerate(datasets):
        labels = [line['dynamic_stance'] for line in split]
        print(names[i], Counter(labels))
        print(out_path)
        with open('data/crosslingual_vaccines/'+out_path+ '/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps(
                    {'_id': line['id_original'] + '_' + line['id_answer'], 'original': line['original_text'],
                     'answer': line['answer_text'], 'label': line['dynamic_stance']}) + "\n")

def main():
    cat_only = True
    do_nl = True

    with open('data/final_dataset.jsonl') as f:
        data = []
        for line in f:
            data.append(json.loads(line))

    vaccines = [line for line in data if line['topic']=='vaccines' and line['dynamic_stance'] not in ['NA', 'Unrelated']]
    for line in vaccines:
        line['lang'] = 'ca'

    random.shuffle(vaccines)
    if cat_only:
        test = vaccines[:500]
        dev = vaccines[501:1001]
        train = vaccines[1002:]
        save_json([test, train, dev], ['test', 'train', 'dev'], "cat_only")

    if do_nl:
        with open('data/final_dataset.jsonl') as f:
            nl_data = []
            for line in f:
                nl_data.append(json.loads(line))
        nl_data = [line for line in nl_data if
                    line['dynamic_stance'] not in ['NA', 'Unrelated']]
        random.shuffle(nl_data)
        for line in nl_data:
            line['lang'] = 'nl'
        vaccines.extend(nl_data)
        ca_test = vaccines[:500]
        nl_test = vaccines[-500:]
        remaining = vaccines[501:-501]
        random.shuffle(remaining)
        dev = remaining[:500]
        train = remaining[501:]
        save_json([ca_test, nl_test, train, dev], ['ca_test', 'nl_test', 'train', 'dev'], "cat_nl")





if __name__ == '__main__':
    main()