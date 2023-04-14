
import csv
import json
import random
from collections import Counter

def save_json(test, train, dev, out_path):
    names = ['test', 'train', 'dev']
    for i, split in enumerate([test, train, dev]):
        with open('data/'+out_path+ '/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps({'_id': line['id_original']+'_'+line['id_answer'], 'original': line['original_text'], 'answer': line['answer_text'], 'label': line['dynamic_stance']}) + "\n")

def get_golden_label(data, key):
    indexes = {'dynamic':{'last':8, 'labels':[4,7]}, 'static':{'last':5, 'labels':[3,4]}}
    for line in data:
        if line[indexes[key]['last']]:
            line.append(line[indexes[key]['last']])
        else:
            labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]]
            line.append(max(set(labels), key=labels.count))
    return data

def main():
    simple = False
    do_topic = False
    include_raco_train = False
    do_topic_with_raco = True
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

    if include_raco_train:
        raco_data = []
        with open('data/annotated/dynamic_stance_forums.csv') as f:
            reader = csv.reader(f)
            for item in reader:
                raco_data.append(item)
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
        with open('data/annotated/dynamic_stance_forums.csv') as f:
            raco_data = []
            reader = csv.reader(f)
            for item in reader:
                raco_data.append(item)
        raco_data = get_golden_label(raco_data, 'dynamic')
        for line in raco_data:
            data.append({'id_original':line[0], 'id_answer':line[1], 'original_text':line[2], 'answer_text':line[3], 'dynamic_stance': line[9], 'topic': ""})
        data = [line for line in data if line['dynamic_stance'] != 'NA']
        random.shuffle(data)
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
            save_json(test, train, dev, 'raco_augment/topic_splits/'+topic)


if __name__ == '__main__':
    main()