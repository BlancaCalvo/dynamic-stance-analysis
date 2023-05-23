
import csv
import json
import random
from collections import Counter
random.seed(2023)

def save_json(test, train, dev, out_path):
    names = ['test', 'train', 'dev']
    for i, split in enumerate([test, train, dev]):
        labels = [line['label'] for line in split]
        print(names[i], Counter(labels))
        print(out_path)
        with open('data/static_data/'+out_path+ '/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps(line) + "\n")

def main():
    simple = True
    do_topic = True

    topics = ['aeroport', 'vaccines', 'lloguer', 'benidormfest', 'subrogada']

    with open('data/final_dataset.jsonl') as f:
        data = []
        for line in f:
            data.append(json.loads(line))

    static_corpus=[]
    done_ids = []
    for line in data:
        if line['id_original'] not in done_ids:
            static_corpus.append({'_id': line['id_original'], 'text': line['original_text'], 'label': line['original_stance'], 'topic':line['topic']})
            done_ids.append(line['id_original'])
        if line['id_answer'] not in done_ids:
            static_corpus.append({'_id': line['id_answer'], 'text': line['answer_text'], 'label': line['answer_stance'], 'topic':line['topic']})
            done_ids.append(line['id_answer'])

    print(len(static_corpus))

    random.shuffle(static_corpus)
    if simple:
        test = static_corpus[:1000]
        dev = static_corpus[1001:2001]
        train = static_corpus[2002:]
        save_json(test, train, dev, "simple_splits")

    if do_topic:
        for topic in topics:
            test = []
            dev = []
            train = []
            count = 0
            for line in static_corpus:
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


if __name__ == '__main__':
    main()