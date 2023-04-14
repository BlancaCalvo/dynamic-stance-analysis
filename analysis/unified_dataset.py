
import csv
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import json

def load_csv(file):
    with open(file) as f:
        read = csv.reader(f)
        data = [line for line in read]
    return data

def save_csv(data, file):
    with open(file, 'w') as o:
        w = csv.writer(o)
        w.writerows(data)

def check_unique_ids(datasets):
    ids_5 = []
    ids_6 = []
   # topic_vaccines_6 = 0
    for key, item in datasets.items():
        if use_print:
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
    if use_print:
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
            if key in ['static', 'emotions']:
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
        if key == 'emotions':
            for line in item:
                labels = []
                for field in [3,4,5]:
                    labels.extend(line[field].split('|'))
                line.append(list(set(labels)))
        else:
            for line in item:
                if line[indexes[key]['last']]:
                    line.append(line[indexes[key]['last']])
                else:
                    labels = line[indexes[key]['labels'][0]:indexes[key]['labels'][1]]
                    line.append(max(set(labels), key=labels.count))
    return datasets

def get_stats_by_topic(datasets, topics, task, remove_na=True):
    indexes = {'dynamic':{'topic':9, 'g_label':10}, 'static':{'topic':1, 'g_label':6}}
    na_static = [line[0] for line in datasets['static'] if line[6] == 'NA']
    results = []
    for topic in topics:
        result = []
        #for key, item in datasets.items():
        if use_print:
            print('\nLabels of {} stance in topic {}'.format(task, topic))
        counts = []
        total = 0
        for line in datasets[task]:
            if line[indexes[task]['topic']] == topic:
                if remove_na and task == 'dynamic':
                    if line[0] in na_static:
                        continue
                counts.append(line[indexes[task]['g_label']])
                total+=1
        for combination, c in Counter(counts).items():
            if use_print:
                print(combination+':', str(round(c/total*100, 2))+'%', c)
            result.append(c/total*100)
        if use_print:
            print('TOTAL:', total)
        results.append(result)
    return results

def get_static_stats_by_type_comment(datasets, topics, type='original'):
    type_index = 1 if type == 'answer' else 0
    id_static_to_label = {}
    results = []
    for line in datasets['static']:
        id_static_to_label[line[0]] = line[6]
    for topic in topics:
        result = []
        counts = []
        total = 0
        if use_print:
            print('\nPosition of {} messages in topic {}'.format(type, topic))
        for line in datasets['dynamic']:
            if line[9] == topic:
                counts.append(id_static_to_label[line[type_index]])
                total += 1
                #if id_static_to_label[line[0]] == 'NA' and id_static_to_label[line[1]] != 'NA':
                #    print()
                #    print(line[2])
                #    print(line[3], id_static_to_label[line[1]])
        for combination, c in Counter(counts).items():
            if use_print:
                print(combination + ':', str(round(c / total * 100, 2)) + '%', c)
            result.append(c/total*100)
        if use_print:
            print('TOTAL:', total)
        results.append(result)
    return results

def get_dynamic_stats_given_static(datasets, labels):
    id_static_to_label = {}
    for line in datasets['static']:
        id_static_to_label[line[0]] = line[6]
    counts = []
    total = 0
    if use_print:
        print('\nDynamic labels of pairs with dynamic original {} and answer {}'.format(labels[0], labels[1]))
    for line in datasets['dynamic']:
        if id_static_to_label[line[0]] == labels[0] and id_static_to_label[line[1]] == labels[1]:
            # if line[10] == 'Disagree':
            #     print('\nOriginal: '+line[2])
            #     print('\nResposta: '+line[3])
            counts.append(line[10])
            total += 1
    for combination, c in Counter(counts).items():
        if use_print:
            print(combination + ':', str(round(c / total * 100, 2)) + '%', c)
    if use_print:
        print('TOTAL:', total)

def plot_labels(results, topics):
    labels = ['FAVOUR', 'AGAINST', 'NEUTRAL', 'NA']
    X_axis = np.arange(len(labels))

    for i, topic in enumerate(topics):
        plt.bar(X_axis - i*0.15, results[i], 0.1, label=topic)

    plt.xticks(X_axis, labels)
    plt.xlabel("Groups")
    plt.ylabel("Number of Students")
    plt.title("Number of Students in each group")
    plt.legend()
    plt.show()

def json_with_all_data(datasets, remove_text=False):
    if remove_text:
        out = '../data/uploading_dataset.jsonl'
    else:
        out = '../data/final_dataset.jsonl'
    id_to_line = {}
    for key, data in datasets.items():
        if key in ['emotions', 'static']:
            id_to_line[key] = {}
            for i,line in enumerate(datasets[key]):
                id_to_line[key][line[0]] = i
    final = []
    for i,line in enumerate(datasets['dynamic']):
        if remove_text:
            original_text = ''
            answer_text = ''
        else:
            original_text = line[2]
            answer_text = line[3]
        final.append({'_id':str(i),
                      'id_original': line[0],
                      'id_answer': line[1],
                      'original_text': original_text,
                      'answer_text': answer_text,
                      'topic': line[9],
                      'dynamic_stance': line[10],
                      'original_stance': datasets['static'][id_to_line['static'][line[0]]][6],
                      'answer_stance': datasets['static'][id_to_line['static'][line[1]]][6],
                      'original_emotion': datasets['emotions'][id_to_line['emotions'][line[0]]][6],
                      'answer_emotion': datasets['emotions'][id_to_line['emotions'][line[1]]][6],
                      })

    with open(out, 'w') as f:
        for line in final:
            f.write(json.dumps(line))
            f.write('\n')


def main():
    global use_print
    use_print = False

    paths = {'static': '../data/annotated/static_stance_2.csv',
             'dynamic': '../data/annotated/dynamic_stance_tweets.csv',
             'emo':  '../data/annotated/emotion_tweets.csv'
             }
    topics = ['vaccines', 'lloguer', 'aeroport',  'subrogada', 'benidormfest']
    datasets = {}
    for key,item in paths.items():
        print(item)
        datasets[key] = load_csv(item)

    datasets['emotions'] = []
    for line in datasets['emo']:
        new_line = [line[1], line[0], line[2], line[3], line[4], line[5]]
        datasets['emotions'].append(new_line)

    matching = check_unique_ids(datasets)
    matching_datasets = keep_only_matching(datasets, matching)
    matching_datasets = assign_topic_to_dynamic(matching_datasets)
    matching_datasets = get_golden_label(matching_datasets)
    save_csv(matching_datasets['dynamic'], '../data/matching/dynamic_stance.csv')
    save_csv(matching_datasets['static'], '../data/matching/static_stance.csv')
    save_csv(matching_datasets['emotions'], '../data/matching/emotion.csv')

    json_with_all_data(matching_datasets)
    json_with_all_data(matching_datasets, remove_text=True)

    # static_stats = get_stats_by_topic(matching_datasets, topics, 'static', remove_na=False)
    # dynamic_stats = get_stats_by_topic(matching_datasets, topics, 'dynamic', remove_na=False)
    #
    # original_static = get_static_stats_by_type_comment(matching_datasets, topics, type='original')
    # answer_static = get_static_stats_by_type_comment(matching_datasets, topics, type='answer')
    #
    # get_dynamic_stats_given_static(matching_datasets, labels=['FAVOUR', 'AGAINST'])
    # get_dynamic_stats_given_static(matching_datasets, labels=['AGAINST', 'FAVOUR'])
    # get_dynamic_stats_given_static(matching_datasets, labels=['FAVOUR', 'FAVOUR'])
    # get_dynamic_stats_given_static(matching_datasets, labels=['AGAINST', 'AGAINST'])
    # get_dynamic_stats_given_static(matching_datasets, labels=['NEUTRAL', 'AGAINST'])
    # get_dynamic_stats_given_static(matching_datasets, labels=['NEUTRAL', 'FAVOUR'])

    #plot_labels(static_stats, topics)

if __name__ == '__main__':
    main()