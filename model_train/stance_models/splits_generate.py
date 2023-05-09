
import csv
import json
import random
from collections import Counter
random.seed(2023)

def save_json(test, train, dev, out_path):
    names = ['test', 'train', 'dev']
    for i, split in enumerate([test, train, dev]):
        with open('data/'+out_path+ '/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps({'_id': line['id_original']+'_'+line['id_answer'], 'original': line['original_text'], 'answer': line['answer_text'], 'label': line['dynamic_stance']}) + "\n")

def get_golden_label(data, key, filter=False):
    indexes = {'dynamic':{'last':8, 'labels':[4,7]}, 'static':{'last':5, 'labels':[3,4]}}
    new_data = []
    for line in data:
        if filter and key == 'dynamic': # filter instances in which there is no consensus of at least 3 of the 4 annotators
            labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]+1]
            if (labels[0] == labels[1] and labels[0] == labels[2]) or (labels[3] == labels[1] and labels[3] == labels[2]) or (labels[3] == labels[0] and labels[3] == labels[2]) or (labels[0] == labels[1] and labels[0] == labels[3]):
                pass
            else:
                continue
        if line[indexes[key]['last']]:
            line.append(line[indexes[key]['last']])
            new_data.append(line)
        else:
            labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]+1]
            line.append(max(set(labels), key=labels.count))
            new_data.append(line)
    return new_data

def main():
    simple = True
    do_topic = True
    include_raco_train = True
    do_topic_with_raco = True
    filtered_raco = True
    topics = ['aeroport', 'vaccines', 'lloguer', 'benidormfest', 'subrogada']

    with open('data/final_dataset.jsonl') as f:
        data = []
        for line in f:
            data.append(json.loads(line))

    data = [line for line in data if line['dynamic_stance'] != 'NA']
    if simple:
        test = data[:1000]
        dev = data[1001:2001]
        train = data[2002:]
        save_json(test, train, dev, "simple_splits")

    if do_topic:
        for topic in topics:
            test = []
            dev = []
            train = []
            count = 0
            for line in data:
                if line['topic'] == topic:
                    test.append(line)
                else:
                    count += 1
                    if count <= 500:
                        dev.append(line)
                    else:
                        train.append(line)
            print(topic, len(train), len(dev), len(test))
            save_json(test, train, dev, 'topic_splits/'+topic)

    raco_data = []
    with open('data/annotated/dynamic_stance_forums.csv') as f:
        reader = csv.reader(f)
        for item in reader:
            raco_data.append(item)
    if include_raco_train:
        raco_data = get_golden_label(raco_data, 'dynamic')
        test = data[:1000]
        remaining = data[1001:]
        for line in raco_data:
            remaining.append({'id_original':line[0], 'id_answer':line[1], 'original_text':line[2], 'answer_text':line[3], 'dynamic_stance': line[9]})
        remaining = [line for line in remaining if line['dynamic_stance'] != 'NA']
        random.shuffle(remaining)
        dev = remaining[:1000]
        train = remaining[1001:]
        save_json(test, train, dev, "raco_augment")

    if do_topic_with_raco:
        raco_data = get_golden_label(raco_data, 'dynamic')
        data_with_raco = data.copy()
        for line in raco_data:
            data_with_raco.append({'id_original':line[0], 'id_answer':line[1], 'original_text':line[2], 'answer_text':line[3], 'dynamic_stance': line[9], 'topic': ""})
        data_with_raco = [line for line in data if line['dynamic_stance'] != 'NA']
        random.shuffle(data_with_raco)
        for topic in topics:
            test = []
            dev = []
            train = []
            count = 0
            for line in data_with_raco:
                if line['topic'] == topic:
                    test.append(line) # test set will be shuffled different than in not agumented, but the entries will be the same
                else:
                    count += 1
                    if count <= 500:
                        dev.append(line)
                    else:
                        train.append(line)
            print(topic, len(train), len(dev), len(test))
            save_json(test, train, dev, 'raco_augment/topic_splits/'+topic)

    if filtered_raco:
        raco_data = get_golden_label(raco_data, 'dynamic', filter=True)
        test = data[:1000]
        remaining = data[1001:]
        for line in raco_data:
            remaining.append(
                {'id_original': line[0], 'id_answer': line[1], 'original_text': line[2], 'answer_text': line[3],
                 'dynamic_stance': line[9]})
        remaining = [line for line in remaining if line['dynamic_stance'] != 'NA']
        random.shuffle(remaining)
        dev = remaining[:1000]
        train = remaining[1001:]
        save_json(test, train, dev, "filtered_raco_augment")

if __name__ == '__main__':
    main()