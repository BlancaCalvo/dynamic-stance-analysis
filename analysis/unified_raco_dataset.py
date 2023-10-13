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

def previous_message(reply_id):
    correspondence = {'1_1':'', '1_2':'1_1', '1_3':'1_2', '2_1':'', '2_2':'2_1', '2_3':'2_2'}
    conversation_id = reply_id.split('_', 1)
    if correspondence[conversation_id[1]] != '':
        new_id = conversation_id[0]+'_'+correspondence[conversation_id[1]]
    else:
        new_id = conversation_id[0]
    return new_id


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

    # emotion labels
    emotions = []
    with open('data/annotated/emotion_raco.csv') as f:
        r = csv.reader(f)
        for line in r:
            emotions.append(line)
    print(len(emotions))

    id_to_line = {}
    for i, line in enumerate(emotions):
        id_to_line[line[1]] = i

    for line in emotions:
        labels = []
        for field in [3, 4, 5]:
            labels.extend(line[field].split('|'))
        line.append(list(set(labels)))

    count_missing = 0
    with open('data/raco_final_dataset.jsonl', 'w') as o:
        for i,line in enumerate(data):
            try:
                o.write(json.dumps({'_id': i,
                                        "id_conversation": line[1],
                                        "id_reply": line[0],
                                        "parent_text": line[2],
                                        "reply_text": line[3],
                                        'dynamic_stance': line[-1],
                                        'parent_emotion': emotions[id_to_line[previous_message(line[0])]][6],
                                        'reply_emotion': emotions[id_to_line[line[0]]][6]
                                        }))
                o.write('\n')
            except KeyError: # some instances miss emotion annotation
                o.write(json.dumps({'_id': i,
                                    "id_conversation": line[1],
                                    "id_reply": line[0],
                                    "parent_text": line[2],
                                    "reply_text": line[3],
                                    'dynamic_stance': line[-1],
                                    'parent_emotion': [],
                                    'reply_emotion': []
                                    }))
                o.write('\n')
                count_missing += 1

    print(count_missing)


if __name__ == '__main__':
    main()