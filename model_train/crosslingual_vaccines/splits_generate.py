
import csv
import json
import random
from collections import Counter
random.seed(2023)

def save_json(datasets, names, out_path):
    for i, split in enumerate(datasets):
        #print(split[0])
        labels = [line['dynamic_stance'] for line in split]
        langs = [line['lang'] for line in split]
        print(names[i], Counter(labels))
        print(names[i], Counter(langs))
        #print(out_path)
        with open('data/crosslingual_vaccines/'+out_path+ '/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps(
                    {'_id': line['id_parent'] + '_' + line['id_reply'], 'parent': line['parent_text'],
                     'reply': line['reply_text'], 'label': line['dynamic_stance']}) + "\n")

def main():
    cat_only = True
    do_nl = True
    few_labels = True

    with open('data/final_dataset.jsonl') as f:
        data = []
        for line in f:
            data.append(json.loads(line))

    vaccines = [line for line in data if line['topic']=='vaccines']
    if not few_labels:
        vaccines = [line for line in vaccines if line['dynamic_stance'] != 'NA']
    else:
        for line in vaccines:
            if line['dynamic_stance'] in ['Query']:
                line['dynamic_stance'] = 'Neutral'
            if line['dynamic_stance'] == 'Agree':
                line['dynamic_stance'] = 'Elaborate'
            if line['dynamic_stance'] == 'Unrelated':
                line['dynamic_stance'] = 'NA'

    for line in vaccines:
        line['lang'] = 'ca'

    random.shuffle(vaccines)
    print('cat_data',len(vaccines))
    if cat_only:
        test = vaccines[:500]
        dev = vaccines[501:1001]
        train = vaccines[1002:]
        save_json([test, train, dev], ['test', 'train', 'dev'], "cat_only")

    if do_nl:
        with open('data/nl/nl_data_revised.jsonl') as f:
            nl_data = []
            for line in f:
                nl_data.append(json.loads(line))
        if not few_labels:
            nl_data = [line for line in nl_data if line['dynamic_stance'] != 'NA']
        else:
            for line in nl_data:
                if line['dynamic_stance'] in ['Query']:
                    line['dynamic_stance'] = 'Neutral'
                if line['dynamic_stance'] == 'Agree':
                    line['dynamic_stance'] = 'Elaborate'
                if line['dynamic_stance'] == 'Unrelated':
                    line['dynamic_stance'] = 'NA'
        random.shuffle(nl_data)
        for line in nl_data:
            line['lang'] = 'nl'
        print('nl_data', len(nl_data))
        dev = nl_data[-500:]
        test = nl_data[:500]
        train = nl_data[501:-501]
        save_json([test, train, dev], ['test', 'train', 'dev'], "nl_only")


        # DOT BOTH
        vaccines.extend(dev)
        vaccines.extend(train)
        print('all', len(vaccines))
        ca_test = vaccines[:500]
        nl_test = test
        remaining = vaccines[501:]
        random.shuffle(remaining)
        dev = remaining[:500]
        train = remaining[501:]
        save_json([ca_test, nl_test, train, dev], ['cat_test', 'nl_test', 'train', 'dev'], "cat_nl")





if __name__ == '__main__':
    main()