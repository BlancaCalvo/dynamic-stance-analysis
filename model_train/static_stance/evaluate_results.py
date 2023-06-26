
import json
import csv
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import pathlib

def get_macro_f1(path_output, path_gold):
    with open(path_output) as f:
        results = []
        r = csv.reader(f, delimiter='\t')
        next(f)
        for line in r:
            results.append(line[1])

    with open(path_gold) as f:
        gold = []
        for line in f:
            gold.append(json.loads(line)['label'])

    #print(len(gold), len(results))
    #print(set(gold))
    print(classification_report(gold, results, zero_division=0))
    print(confusion_matrix(gold, results))
    return (f1_score(gold, results, average='macro'), len(gold))

def main():
    models = ['roberta-large-ca-v2', 'mdeberta-v3-base'] # 'roberta-base-ca-v2',
    topics = ['vaccines', 'lloguer', 'aeroport',  'subrogada', 'benidormfest']
    outputs_path = 'output/stance_data/static_stance/output/'

    table_simple_results = {}
    for model in models:
        table_simple_results[model] = []
        path = list(pathlib.Path(outputs_path+model+'/simple_splits').glob('St*/test_results_tecla.txt'))[0]
        table_simple_results[model].append(get_macro_f1(path, 'data/static_data/simple_splits/test.jsonl'))
        exit()

    for key, entry in table_simple_results.items():
        print(key + ' & '+ str(round(entry[0][0], 2)) + ' & ' + str(entry[0][1]) + ' \\\\')

    table_topic_results = {}
    for model in models:
        for topic in topics:
            table_topic_results[(model, topic)] = []
            path = list(pathlib.Path(outputs_path+model+'/topic_splits/'+topic).glob('St*/*.txt'))[-1]
            table_topic_results[(model,topic)].append(get_macro_f1(path, 'data/static_data/topic_splits/'+topic+'/test.jsonl'))

    for key, entry in table_topic_results.items():
        print(key[0] + ' & '+ key[1] + ' & ' + str(round(entry[0][0], 2)) + ' & ' + str(entry[0][1]) + ' \\\\')


main()