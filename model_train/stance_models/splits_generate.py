
import csv
import json
import random
from collections import Counter

def save_json(test, train, dev, names):
    for i, split in enumerate([test, train, dev]):
        with open('data/random_splits/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps({'_id': line[0]+'_'+line[1], 'original': line[2], 'answer': line[3], 'label': line[9]}) + "\n")

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
    do_topic = False
    include_raco = True
    topics = ['aeroport', 'vaccines', 'lloguer', 'benidormfest', 'subrogada']
    if do_topic:
        tweets_path = 'data/matching/dynamic_stance.csv'
    else:
        tweets_path = 'data/annotated/dynamic_stance_tweets.csv'

    data = []
    with open (tweets_path) as f:
        reader = csv.reader(f)
        for item in reader:
            data.append(item)

    if include_raco and not do_topic:
        with open('data/annotated/dynamic_stance_forums.csv') as f:
            reader = csv.reader(f)
            for item in reader:
                data.append(item)
    #exit()
    data = get_golden_label(data, 'dynamic')
    random.shuffle(data)

    if do_topic:
        for topic in topics:
            test = []
            dev = []
            train = []
            count = 0
            for line in data:
                if line[9] == topic:
                    test.append(line)
                else:
                    count += 1
                    if count <= 500:
                        dev.append(line)
                    else:
                        train.append(line)
            names = ['test_'+topic, 'train_'+topic, 'dev_'+topic]
            print(topic, len(train), len(test), len(dev))
            save_json(test, train, dev, names)
    else:
        test = data[:1000]
        dev = data[1001:2001]
        train = data[2002:]
        names = ['test', 'train', 'dev']
        save_json(test, train, dev, names)

main()