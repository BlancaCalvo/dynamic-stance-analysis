import json
from collections import Counter
import sys


def main():
    dynamic_labels = ['Agree', 'Disagree', 'Elaborate', 'Query', 'Neutral', 'Unrelated', 'NA']

    with open(sys.argv[1]) as f:
        data=[]
        for line in f:
            data.append(json.loads(line))
    print(data[0])

    labels = []
    for line in data:
        labels.append(line['dynamic_stance'])
    print(len(labels))
    c = Counter(labels)
    for i in dynamic_labels:
        for key, item in c.items():
            if key == i:
                print('\\bf', key, '&', item, '('+str(round(item/len(labels)*100, 2))+'\\%)')




if __name__ == '__main__':
    main()