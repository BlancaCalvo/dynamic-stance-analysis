import csv
import json

def get_golden_label(data, key='dynamic'):
    indexes = {'dynamic':{'last':8, 'labels':[4,7]}}
    for line in data:
        if line[indexes[key]['last']]:
            line.append(line[indexes[key]['last']])
        else:
            labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]]
            line.append(max(set(labels), key=labels.count))
    return data

def main():
    data = []
    with open('data/annotated/dynamic_stance_forums.csv') as f:
        r = csv.reader(f)
        next(r)
        for line in r:
            data.append(line)
    print(len(data))
    print(data[0])

    data = get_golden_label(data)
    print(len(data))

    # TODO: also add emotions labels

    with open('data/raco_final_dataset.jsonl', 'w') as o:
        for i,line in enumerate(data):
            o.write(json.dumps({'_id': i,
                                "id_conversation": line[1],
                                "id_reply": line[0],
                                "parent_text": line[2],
                                "reply_text": line[3],
                                'dynamic_stance': line[-1]}))
            o.write('\n')

if __name__ == '__main__':
    main()