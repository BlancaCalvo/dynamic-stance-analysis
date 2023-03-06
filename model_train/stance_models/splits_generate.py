
import csv
import json
import random
from collections import Counter

def main():
    data = []
    with open('data/matching/dynamic_stance.csv') as f:
        reader = csv.reader(f)
        for item in reader:
            data.append(item)

    random.shuffle(data)

    # half of the test should be pairs that where never seen in train

    test = data[:1000]
    dev = data[1001:2001]
    train = data[2002:]

    names = ['test', 'train', 'dev']

    for i, split in enumerate([test, train, dev]):
        with open('data/random_splits/'+names[i] + '.jsonl', 'w') as file:
            for line in split:
                file.write(json.dumps({'_id': line[0]+'_'+line[1], 'original': line[2], 'answer': line[3], 'label': line[10]}) + "\n")

main()