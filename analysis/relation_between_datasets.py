import csv
from collections import Counter

def load_csv(file):
    with open(file) as f:
        read = csv.reader(f)
        data = [line for line in read]
    return data

def check_unique_ids(datasets):
    ids_5 = []
    ids_6 = []
   # topic_vaccines_6 = 0
    for key, item in datasets.items():
        print(key+":", len(item))
        if key.startswith('dynamic'):
            for line in item:
                ids_5.append(line[0])
                ids_5.append(line[1])
        if key.startswith('static'):
            for line in item:
                ids_6.append(line[0])
                #if line[1] == 'vaccines':
                #    topic_vaccines_6 += 1

    matching = [name for name in ids_5 if name in ids_6]
    unique = list(set(matching))
    print('Unique matching ids:', len(unique))
    print('Unique ids in the dynamic stance dataset:', len(list(set(ids_5))))
    print('Unique ids in the static stance dataset:', len(list(set(ids_6))))
    return unique

def keep_only_matching(datasets, matching):
    matching_datasets = {}
    for key, item in datasets.items():
        matching_datasets[key] = []
        for line in item:
            if key == 'dynamic':
                if line[0] in matching and line[1] in matching:
                    matching_datasets[key].append(line)
            if key == 'static':
                if line[0] in matching:
                    matching_datasets[key].append(line)
    return matching_datasets

def assign_topic_to_dynamic(datasets):
    id_topic_dict={}
    for line in datasets['static']:
        id_topic_dict[line[0]] = line[1]
    for line in datasets['dynamic']:
        line.append(id_topic_dict[line[0]])

    return datasets

def get_golden_label(datasets):
    indexes = {'dynamic':{'last':8, 'labels':[4,7]}, 'static':{'last':5, 'labels':[3,4]}}
    for key, item in datasets.items():
        for line in item:
            if line[indexes[key]['last']]:
                line.append(line[indexes[key]['last']])
            else:
                labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]]
                line.append(max(set(labels), key=labels.count))
    return datasets

def get_stats_by_topic(datasets, topics, remove_na=True):
    indexes = {'dynamic':{'topic':9, 'g_label':10}, 'static':{'topic':1, 'g_label':6}}
    na_static = [line[0] for line in datasets['static'] if line[6] == 'NA']
    for topic in topics:
        for key, item in datasets.items():
            print('\nLabels of {} stance in topic {}'.format(key, topic))
            counts = []
            total = 0
            for line in item:
                if line[indexes[key]['topic']] == topic:
                    if remove_na and key == 'dynamic':
                        if line[0] in na_static:
                            continue
                    counts.append(line[indexes[key]['g_label']])
                    total+=1
            for combination, c in Counter(counts).items():
                print(combination+':', str(round(c/total*100))+'%', c)
            print('TOTAL:', total)

def get_static_stats_by_type_comment(datasets, topics, type='original'):
    type_index = 1 if type == 'answer' else 0
    id_static_to_label = {}
    for line in datasets['static']:
        id_static_to_label[line[0]] = line[6]
    for topic in topics:
        counts = []
        total = 0
        print('\nPosition of {} messages in topic {}'.format(type, topic))
        for line in datasets['dynamic']:
            if line[9] == topic:
                counts.append(id_static_to_label[line[type_index]])
                total += 1
        for combination, c in Counter(counts).items():
            print(combination + ':', str(round(c / total * 100)) + '%', c)
        print('TOTAL:', total)

def get_dynamic_stats_given_dynamic(datasets, labels):
    id_static_to_label = {}
    for line in datasets['static']:
        id_static_to_label[line[0]] = line[6]
    counts = []
    total = 0
    print('\nDynamic labels of pairs with dynamic original {} and answer {}'.format(labels[0], labels[1]))
    for line in datasets['dynamic']:
        if id_static_to_label[line[0]] == labels[0] and id_static_to_label[line[1]] == labels[1]:
            counts.append(line[10])
            total += 1
    for combination, c in Counter(counts).items():
        print(combination + ':', str(round(c / total * 100)) + '%', c)
    print('TOTAL:', total)



def main():

    paths = {'static': '../data/annotated/static_stance_tweets.csv',
             'dynamic': '../data/annotated/dynamic_stance_tweets.csv'
             }
    topics = ['aeroport', 'vaccines', 'lloguer', 'benidormfest', 'subrogada']
    datasets = {}
    for key,item in paths.items():
        print(item)
        datasets[key] = load_csv(item)

    matching = check_unique_ids(datasets)
    matching_datasets = keep_only_matching(datasets, matching)
    matching_datasets = assign_topic_to_dynamic(matching_datasets)
    matching_datasets = get_golden_label(matching_datasets)
    #print(matching_datasets['static'][4])
    #print(matching_datasets['dynamic'][800])

    #get_stats_by_topic(matching_datasets, topics)
    get_stats_by_topic(matching_datasets, topics, remove_na=False)

    get_static_stats_by_type_comment(matching_datasets, topics, type='original')
    get_static_stats_by_type_comment(matching_datasets, topics, type='answer')

    get_dynamic_stats_given_dynamic(matching_datasets, labels=['FAVOUR', 'AGAINST'])
    get_dynamic_stats_given_dynamic(matching_datasets, labels=['AGAINST', 'FAVOUR'])
    get_dynamic_stats_given_dynamic(matching_datasets, labels=['FAVOUR', 'FAVOUR'])
    get_dynamic_stats_given_dynamic(matching_datasets, labels=['AGAINST', 'AGAINST'])
    get_dynamic_stats_given_dynamic(matching_datasets, labels=['NEUTRAL', 'AGAINST'])
    get_dynamic_stats_given_dynamic(matching_datasets, labels=['NEUTRAL', 'FAVOUR'])



main()