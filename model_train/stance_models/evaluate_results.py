
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
    models = ['roberta-large-ca-v2', 'mdeberta-v3-base'] # 'roberta-base-ca-v2', 'mbert',
    topics = ['vaccines', 'lloguer', 'aeroport',  'subrogada', 'benidormfest']

    table_simple_results = {}
    for model in models:
        table_simple_results[model] = []
        path = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/stance_models/output/'+model+'/simple_splits').glob('Dy*/*.txt'))[0]
        table_simple_results[model].append(get_macro_f1(path, 'data/simple_splits/test.jsonl'))

        path_2 = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/stance_models/output/' + model + '/raco_augment').glob('Dy*/*.txt'))[-1]
        table_simple_results[model].append(get_macro_f1(path_2, 'data/simple_splits/test.jsonl')) #it's the same test set

        #path_3 = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/stance_models/output/' + model + '/focal_loss').glob(
        #         'Dy*/*.txt'))[-1]
        #table_simple_results[model].append(get_macro_f1(path_3, 'data/simple_splits/test.jsonl'))  # it's the same test set

    for key, entry in table_simple_results.items():
        print(key + ' & '+ str(round(entry[0][0], 2)) + ' & '+ str(round(entry[1][0], 2)) + ' & ' + str(entry[0][1]) + ' \\\\')

    table_topic_results = {}
    for model in models:
        for topic in topics:
            table_topic_results[(model, topic)] = []
            path = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/stance_models/output/'+model+'/topic_splits/'+topic).glob('Dy*/*.txt'))[-1]
            table_topic_results[(model,topic)].append(get_macro_f1(path, 'data/topic_splits/'+topic+'/test.jsonl'))

            path_2 = list(pathlib.Path('output/gpfs/scratch/bsc88/bsc88080/stance_models/output/' + model + '/raco_augment/topic_splits/' + topic).glob('Dy*/*.txt'))[0]
            table_topic_results[(model, topic)].append(get_macro_f1(path_2, 'data/raco_augment/topic_splits/' + topic + '/test.jsonl'))

    for key, entry in table_topic_results.items():
        print(key[0] + ' & '+ key[1] + ' & ' + str(round(entry[0][0], 2)) + ' & ' + str(round(entry[1][0], 2)) + ' & ' + str(entry[0][1]) + ' \\\\')


main()