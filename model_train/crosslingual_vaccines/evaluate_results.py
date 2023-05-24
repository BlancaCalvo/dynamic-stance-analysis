
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
    #print(classification_report(gold, results, zero_division=0))
    #print(confusion_matrix(gold, results))
    return (f1_score(gold, results, average='macro'), len(gold))

def main():
    models = ['mdeberta-v3-base'] # 'roberta-base-ca-v2', 'mbert',
    #topics = ['vaccines', 'lloguer', 'aeroport',  'subrogada', 'benidormfest']

    table_simple_results = {}
    for model in models:
        table_simple_results[model] = []
        path = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/crosslingual_vaccines/output/'+model+'/cat_only').glob('Dy*/*.txt'))[0]
        table_simple_results[model].append(get_macro_f1(path, 'data/crosslingual_vaccines/cat_only/test.jsonl'))

        path_2 = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/crosslingual_vaccines/output/' + model + '/cat_nl').glob('Dy*/*.txt'))[-1]
        table_simple_results[model].append(get_macro_f1(path_2, 'data/crosslingual_vaccines/cat_nl/ca_test.jsonl'))

    for key, entry in table_simple_results.items():
        print(key + ' & '+ str(round(entry[0][0], 2)) + ' & '+ str(round(entry[1][0], 2)) + ' & ' + str(entry[0][1]) + ' \\\\')



main()