
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
    model = 'mdeberta-v3-base' # 'roberta-base-ca-v2', 'mbert',
    #topics = ['vaccines', 'lloguer', 'aeroport',  'subrogada', 'benidormfest']
    samples = ['cat_only', ('cat_nl', 'cat'), ('cat_nl', 'nl')]

    table_simple_results = {}
    for sample in samples:
        table_simple_results[sample] = []
        if sample == 'cat_only':
            path = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/crosslingual_vaccines/output/'+model+'/'+sample).glob('Dy*/*.txt'))[0]
            table_simple_results[sample].append(get_macro_f1(path, 'data/crosslingual_vaccines/'+sample+'/test.jsonl'))
        else:
            path = 'output/gpfs/scratch/bsc88/bsc88080/crosslingual_vaccines/output/'+model+'/'+ sample[0]+'/results_'+sample[1]+'.txt'
            table_simple_results[sample].append(
                get_macro_f1(path, 'data/crosslingual_vaccines/' + sample[0] + '/'+sample[1]+'_test.jsonl'))

    for key, entry in table_simple_results.items():
        print(str(key) + ' & '+ str(round(entry[0][0], 2)) + ' & ' + str(entry[0][1]) + ' \\\\')



main()