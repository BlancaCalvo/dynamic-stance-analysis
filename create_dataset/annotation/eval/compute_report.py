
# common
import sys
import argparse
import collections
from itertools import combinations

# data formats
import csv
import json

# statistics
from sklearn.metrics import cohen_kappa_score, confusion_matrix, mean_squared_error
from statsmodels.stats import inter_rater as irr
from scipy import spatial
from nltk.metrics.agreement import AnnotationTask
import numpy as np

# own
from funcions_spans import spans_iaa

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

def parsing_arguments(parser):
    parser.add_argument("--data", type=str, default='', nargs='+')
    parser.add_argument("--referee", action='store_true', help='Mark if one of the files is from the referee, only makes sense in task 1')
    parser.add_argument("--task", type=str, required=True)
    parser.add_argument("--metrics", type=str, default=None)
    parser.add_argument("--span_level", type=str, default='token', choices=['token', 'string']) # char is not implemented
    return parser

def load_task_1(f, referee=False, keep=None):
    data_all = json.load(f)
    data = {'Polar_expression':[], 'Source':[], 'Target':[], 'Polarity':[], 'Intensity':[]}
    existing_ids = []
    for i, line in enumerate(data_all):
        if referee:
            existing_ids.append(line['sent_id'])
            if keep:
                if line['sent_id'] not in keep:
                    continue
        for span in ['Polar_expression', 'Source', 'Target']:
            expressions = []
            for opinion in line['opinions']:
                try:
                    expressions.append(opinion[span][0][0].lower())
                except IndexError:
                    continue
            data[span].append(expressions)
        for label in ['Polarity', 'Intensity']:
            labels = []
            for opinion in line['opinions']:
                try:
                    labels.append(opinion[label])
                except IndexError:
                    continue
            data[label].append(labels)
    if referee and not keep:
        return data, existing_ids
    else:
        return data

def load_data(task, data, referee=False):
    out = []
    if task == '1':
        if referee:
            f = open(data[1])
            single, keep = load_task_1(f, referee)
            out.append(single)
            f = open(data[0])
            out.append(load_task_1(f, referee, keep))
        else:
            for path in data:
                f = open(path)
                out.append(load_task_1(f, referee))
    else:
        with open(data[0], 'r', encoding="latin1") as file:
            content = csv.reader(file, quotechar='"')
            next(content, None)
            data_all = list(content)
        relevant_label = {'2':3, '3':4, '4':3, '5':4, '6':3}
        if task in ['2', '4']:
            for line in data_all:
                instance = []
                for element in line[relevant_label[task]:len(line)]:
                    instance.append(element.split('|'))
                out.append(instance)
        else:
            for line in data_all:
                out.append(line[relevant_label[task]:len(line)])

    return out

def dict_for_each_ann(n_annotators):
    output = {}
    names_dicts = []
    for an in range(n_annotators):
        names_dicts.append(an)
        output[an] = []
    return output, names_dicts


def create_label_vectors(data, labels): # MultiLabelBinarizer().fit_transform(data) binarizes per instance and not per label
    matrix = []
    for label in labels:  # por cada label, vamos por todas las instancias y miramos si están
        vector = []
        for line in data:
            if label in line:
                vector.append(1)
            else:
                vector.append(0)
        matrix.append(vector)
    return matrix



def evaluate_cohen(matrix1, matrix2, labels, multi=False, mse=False):
    score_labels = {}
    if not multi:
        for i, label in enumerate(labels):
            #if matrix1[i] != [0] * len(matrix2[i]): # if vector not empty, this should never happen
            if mse:
                score_labels[label] = mean_squared_error(
                    np.array(matrix1[i]), np.array(matrix2[i]))
            else:
                score_labels[label] = cohen_kappa_score(
                    np.array(matrix1[i]), np.array(matrix2[i]))
                #print(F'Cohen\' kappa for \'{label}\': {score_labels[label]}')

        score_labels_avg = np.mean(list(score_labels.values()))
        score_labels.update({'single-label-average': score_labels_avg})
        #print(f'Average cohen\' kappa: {score_labels_avg}')
        return score_labels
    else:
        # Add task data for the annotators pair
        task_data = []
        for i, entry in enumerate(matrix1):
            annotation = 'coder_a', i, tuple(entry)
            task_data.append(annotation)
        for i, entry in enumerate(matrix2):
            annotation = 'coder_b', i, tuple(entry)
            task_data.append(annotation)

        # https://www.nltk.org/_modules/nltk/metrics/agreement.html
        cosine_task = AnnotationTask(data=task_data, distance=cosine_distance)
        score = cosine_task.kappa()
        #score_labels['multi-label-cosine'] = score
        #print(f"Cohen's Kappa using Cosine distance: {score}")

        return score


def cosine_distance(vec1, vec2):
    distance = spatial.distance.cosine(vec1, vec2)
    return distance



def evaluate_exact_cohen(data, index1, index2):
    score_labels = {}
    classes1 = [str(sorted(d[index1])) for d in data]
    classes2 = [str(sorted(d[index2])) for d in data]
    score = cohen_kappa_score(classes1, classes2)
    #score_labels['multi-label-exact'] = score
    #print('Exact Cohen\'s Kappa', cohen_kappa_score(
    #    annotations[list_annotators[0]], annotations[list_annotators[1]]))
    return score

def iaa_single(data, index1, index2, last=False):
    if last:
        classes1 = []
        classes2 = []
        for d in data:
            if d[index2]:
                classes1.append(d[index1])
                classes2.append(d[index2])
            else:
                classes1.append(d[index1])
                classes2.append(d[index1])
    else:
        classes1 = [d[index1] for d in data]
        classes2 = [d[index2] for d in data]
    agreement = cohen_kappa_score(classes1, classes2)
    print('Agreement between annotator {} and {}: {}'.format(index1+1, index2+1, agreement))
    if agreement < 0.7:
        result_matrix = [list(set(classes1))]
        confusion = [list(a) for a in confusion_matrix(classes1, classes2, labels=result_matrix[0])]
        result_matrix.extend(confusion)
        #print(np.array(result_matrix))
    return classes1, classes2

def iaa_multi(data, index1, index2, labels, list_metrics):
    classes1 = [d[index1] for d in data]
    classes2 = [d[index2] for d in data]
    print('\n')
    print('BETWEEN ANNOTATOR {} AND {}'.format(index1+1, index2+1))
    matrix1 = create_label_vectors(classes1, labels)
    matrix2 = create_label_vectors(classes2, labels)
    if 'single_cohen' in list_metrics:
        #print(evaluate_cohen(matrix1, matrix2, labels))
        print('IAA by label is: {}'.format(evaluate_cohen(matrix1, matrix2, labels)))

    # FOR EACH ANNOTATION, SEE HOW SIMILAR THE ANNOTATIONS ARE (VECTOR SIMILARITY APPROACH)
    if 'multi_cohen' in list_metrics:
        #print(evaluate_cohen(matrix1, matrix2, labels, multi=True))
        print('IAA measured as vector similarity of labels is {}'.format(evaluate_cohen(matrix1, matrix2, labels, multi=True)))
        # there is a warning, but it might be because of the zeros
        # issue when there is few data: 0s are also counted as similarity
        # TODO: what if we do this per instance instead of per label and then do multi kappa: https://stats.stackexchange.com/questions/511927/interrater-reliability-with-multi-rater-multi-label-dataset


        # FOR EACH ANNOTATION, SEE IF THE LABELS ARE EXACTLY THE SAME
    if 'exact_cohen' in list_metrics:
        #print(evaluate_exact_cohen(data, index1, index2))
        print('Exact match IAA is {}'.format(evaluate_exact_cohen(data, index1, index2)))
    return matrix1, matrix2

def print_distribution(data, task, n_ann):
    print('\n')
    print('Instances annotated:', len(data))
    print("")
    print('LABELS DISTRIBUTION')
    all_labels = []
    for i in range(n_ann):
        print('\n')
        print('ANNOTATOR', i+1)
        if task != '1':
            if task in ['2', '4']:
                for line in data:
                    all_labels.extend(line[i])
            elif task in ['3', '5', '6']:
                for line in data:
                    all_labels.append(line[i])
            counter = collections.Counter(all_labels)
            for key, value in counter.items():
                print('Label {}: {}{}'.format(key, round(value/len(all_labels)*100, 2), '%'))
        else:
            for labels in data[i]['Polarity']:
                all_labels.extend(labels)
            for labels in data[i]['Intensity']:
                all_labels.extend(labels)
            counter = collections.Counter(all_labels)
            for key, value in counter.items():
                print('Label {}: {}{}'.format(key, round(value/(len(all_labels)/2)*100, 2), '%'))

def calculate_fleiss(results, n_ann):
    data = np.unique(np.array(results), axis=0) # assumes all annotations will be different, if not, asser fails
    assert len(data) == n_ann
    matrix = np.array(data)
    transposed = matrix.transpose()
    agg = irr.aggregate_raters(transposed)  # returns a tuple (data, categories)
    fleiss = irr.fleiss_kappa(agg[0], method='fleiss')
    print("\nOverall Fleiss' Kappa between the {} main annotators: {}".format(transposed.shape[1], fleiss))

def calculate_fleiss_multi(results, labels, n_ann):
    print('\n')
    print('FLEISS KAPPA PER LABELS')
    data = np.unique(np.array(results), axis=0)  # assumes all annotations will be different, if not, assert fails
    assert len(data) == n_ann
    for i,lab in enumerate(labels): # for each label
        compare =[]
        for an in range(len(data)):
            compare.append(data[an][i])
        matrix = np.array(compare)
        transposed = matrix.transpose()
        agg = irr.aggregate_raters(transposed)  # returns a tuple (data, categories)
        fleiss = irr.fleiss_kappa(agg[0], method='fleiss')
        print("Fleiss' Kappa label {} between the {} annotators: {}".format(lab, transposed.shape[1], fleiss))


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    data = load_data(args.task, args.data, args.referee)
    if args.task == '1':
        n_ann = len(data)
    else:
        n_ann = len(data[0])

    print_distribution(data, args.task, n_ann)

    if args.task in ['3','5','6']: # stance
        print('\n')
        print('IAA BETWEEN ANNOTATORS')
        referee = n_ann-1  # assumes referee is always the last annotator
        annotators = list(range(0, len(data[0])))
        compare = list(combinations(annotators, 2))
        all_results = []
        for comp in compare:
            if comp[1] == referee:
                iaa_single(data, comp[0], comp[1], last=True)
            else:
                c1, c2 = iaa_single(data, comp[0], comp[1])
                all_results.append(c1)
                all_results.append(c2)
        calculate_fleiss(all_results, n_ann-1)

    elif args.task in ['2','4']: # emotions
        all_results = []
        if args.metrics == None:
            metrics = ['single_cohen', 'multi_cohen', 'exact_cohen']
        else:
            metrics = args.metrics
        labels = ['joy', 'disgust', 'anger', 'sadness', 'anticipation', 'fear', 'distrust', 'surprise', 'no emotion', 'na']
        for i, _ in enumerate(data[0]):
            try:
                m1, m2 = iaa_multi(data, i, i + 1, labels, list_metrics=metrics)
                all_results.append(m1)
                all_results.append(m2)
            except IndexError:
                m1, m2 = iaa_multi(data, 0, i, labels, list_metrics=metrics)
                all_results.append(m1)
                all_results.append(m2)
                continue
        calculate_fleiss_multi(all_results, labels, n_ann)

    elif args.task in ['1']: # polarity
        print('\n')
        print('IAA BETWEEN ANNOTATORS')
        for span in ['Polar_expression', 'Source', 'Target']:
            all_iaa = []
            for i,line in enumerate(data[0][span]):
                all_iaa.append(spans_iaa(line, data[1][span][i], args.span_level))
            print('Average IAA of {} is {}'.format(span, sum(all_iaa)/len(all_iaa)))
        for label in ['Polarity', 'Intensity']:
            if label == 'Polarity':
                labels = ['Positive', 'Negative', 'Neutral']
            else:
                labels = ['Strong', 'Standard']
            all_labels = [[],[]]
            for i,line in enumerate(data[0][label]):
                all_labels[0].append(line)
                all_labels[1].append(data[1][label][i])
            matrices = []
            for list_labels in all_labels:
                matrices.append(create_label_vectors(list_labels, labels))
            print('IAA by label of {} is: {}'.format(label, evaluate_cohen(matrices[0], matrices[1], labels)))
            print('MSE by label of {} is: {}'.format(label, evaluate_cohen(matrices[0], matrices[1], labels, mse=True)))
            print('IAA measured as vector similarity of labels of {} is {}'.format(label,
                evaluate_cohen(matrices[0], matrices[1], labels, multi=True)))
            #print('Exact match IAA of {} is {}'.format(label, evaluate_exact_cohen(all_labels, 0, 1)))
    else:
        print('this is not a task')



if __name__ == '__main__':
    main()
