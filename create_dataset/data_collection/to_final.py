import csv
import argparse
import random
from nltk.tokenize import word_tokenize
from language_detector import detect_language
import re

def clean(text):
    tokenized = word_tokenize(text)
    clean = [word for word in tokenized if word.isalpha() and not re.match(r'@[a-zA-Z0-9_]+', word)
             and not re.match(r'#[a-zA-Z0-9_]+', word) and not re.match('https', word) and not re.match(r'//t\.co/[a-zA-Z0-9_/]+', word)]
    return clean

def detect_lang(text):
    lang_dect = detect_language(text)
    #print(lang_dect)
    return lang_dect['pref_lang']

def check_length_and_lang(tuit, lang, pair=True):
    good = True
    if pair:
        if len(clean(tuit[2])) < 8 or len(clean(tuit[3])) < 8: # tokenize, remove hashtags, users and urls and count more than 8 tokens for both texts
            good = False
        if detect_lang(tuit[2]) != lang and detect_lang(tuit[3]) != lang: # here just if both are in other languages
            good = False
        if tuit[7] == tuit[8]: # remove if the user id answering himself (thread)
            good = False
    else:
        if len(clean(tuit[1])) < 8:
            good = False

    return good

def list_duplicates_of(seq,item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item,start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", type=str, required=False)
    parser.add_argument("--lang", type=str, default='ca', required=False)
    parser.add_argument("--directory", type=str, default="data/", required=False)
    args = parser.parse_args()
    print(args)

    final_tuits = []
    final_pairs = []
    for topic in args.topics.split(' '):

        filtered_pairs = []
        all_tuits = []
        with open(args.directory+'paired_tweets_'+topic+'.csv', 'r') as file:
            print('\n', topic)
            content = csv.reader(file, quotechar='"')
            tuits = list(content)
            print('Imported pairs',len(tuits))

            # deduplicate pairs
            u_tuits = [list(x) for x in set(tuple(x) for x in tuits)]
            print('Deduplicated pairs', len(u_tuits))

            for pair_tuit in u_tuits:
                good_pairs = check_length_and_lang(pair_tuit, args.lang)
                if good_pairs:
                    filtered_pairs.append(pair_tuit)
                    all_tuits.append(pair_tuit[2])
                    all_tuits.append(pair_tuit[3])
                #else:
                #    print(pair_tuit)
            print('Filtered pairs',len(filtered_pairs))
            print('Filtered tuits', len(set(all_tuits)))
            #print(len(set(all_tuits)))
            #if len(set(all_tuits)) > 2500: # eliminem el filtre
            #    filtered_pairs = random.sample(filtered_pairs, 1500)

            # elif len(set(all_tuits)) < 2000: # in case we don't have enough tweets we get the ones that do not have answers
            #     with open('data/no_answer_' + topic + '.csv', 'r') as file:
            #         content = csv.reader(file, quotechar='"')
            #         no_answer_tuits = list(content)
            #     to_add = [tuit for tuit in no_answer_tuits if check_length_and_lang(tuit, pair=False)]
            #     to_add = [list(x) for x in set(tuple(x) for x in to_add)]
            #     if len(to_add) > 2000-len(set(all_tuits)):
            #         to_add = random.sample(to_add, 2000-len(set(all_tuits)))
            #     for tuit in to_add:
            #         tuit = tuit[:-1] # I remove conversation id from the final corpus
            #         tuit.append(topic)
            #         tuit.append('no_pair')
            #         final_tuits.append(tuit)
            #     print(topic+' added single tuits:',len(to_add))

            print('Chosen pairs', len(filtered_pairs))
            for pair in filtered_pairs:
                from_main = [pair[0], pair[2], pair[4], topic, 'pair']
                final_tuits.append(from_main)
                from_answer = [pair[1], pair[3], pair[5], topic, 'pair']
                final_tuits.append(from_answer)
        #print(topic,len([list(x) for x in set(tuple(x) for x in final_tuits)]))
        final_pairs.extend(filtered_pairs)

    unique_ids = list(set(x[0] for x in final_tuits))
    #print(unique_ids)
    unique_tuits = []
    for tuit in final_tuits:
        if tuit[0] in unique_ids:
            unique_tuits.append(tuit)
            unique_ids.remove(tuit[0])
        #print(len(unique_ids))
    #unique_tuits = [list(x) for x in set(tuple(x[0]) for x in final_tuits)]
    print('\n')
    print('Total tuits',len(unique_tuits))

    with open(args.directory+'corpus_tuits.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for line in unique_tuits:
            wr.writerow(line)

    print('Sum from all pairs', len(final_pairs))
    # # check if there are duplicated pairs
    # unique_pairs = [list(x) for x in set(tuple(x) for x in final_pairs)]
    # print('After removing duplicated',len(unique_pairs))
    #
    # # already_there = []
    # for x in final_pairs:
    #     if x in already_there:
    #         print(x)
    #         #print(final_pairs[list_duplicates_of(final_pairs, x)[0]], final_pairs[list_duplicates_of(final_pairs, x)[1]])
    #     else:
    #         already_there.append(x)

    with open(args.directory+'corpus_paired_tuits.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for line in final_pairs:
            wr.writerow(line)


if __name__ == '__main__':
    main()