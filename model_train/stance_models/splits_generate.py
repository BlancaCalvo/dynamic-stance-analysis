
import csv
import json
from collections import Counter

def save_json(test, train, dev, names):
    for i, split in enumerate([test, train, dev]):
        with open('data/random_splits/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps({'_id': line['id_original']+'_'+line['id_answer'], 'original': line['original_text'], 'answer': line['answer_text'], 'label': line['dynamic_stance']}) + "\n")

def main():
    do_topic = True
    include_raco_train = True
    topics = ['aeroport', 'vaccines', 'lloguer', 'benidormfest', 'subrogada']

    with open('data/final_dataset.jsonl') as f:
        data = []
        for line in f:
            data.append(json.loads(line))

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