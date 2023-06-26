import csv
import json

def get_golden_label(data, key='dynamic'):
    indexes = {'dynamic':{'last':6, 'labels':[4,5]}}
    for line in data:
        if line[indexes[key]['last']]:
            line.append(line[indexes[key]['last']])
        else:
            labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]]
            line.append(max(set(labels), key=labels.count))
    return data

def main():
    nl_data = []
    with open('root_reply_gold_standard_nl_clean.tsv') as f:
        r = csv.reader(f, delimiter='\t')
        next(r)
        for line in r:
            nl_data.append(line)
    print(len(nl_data))
    #nl_data = get_golden_label(nl_data)

    with open('nl_data.jsonl', 'w') as o:
        for i,line in enumerate(nl_data):
            if line[4] != 'Unrelated':
                o.write(json.dumps({'_id':i, "id_original": line[0], "id_answer": line[2], "original_text":line[1], "answer_text":line[3], 'topic':'vaccines', 'dynamic_stance':line[5]}))
                o.write('\n')

if __name__ == '__main__':
    main()