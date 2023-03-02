import tweepy as tw
import csv
import argparse
import glob
from twitter_credentials import token_academic
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", default='vaccines', type=str, required=False)
    args = parser.parse_args()
    print(args)
    return args

def load_all(args):

    # for all csvs in the folder, do this and put it in a single file
    total_list = []
    for topic in args.topics.split(' '):
        for f in glob.glob('data/initial_collection/tweets_*_' + topic + '.csv'):
            with open(f, 'r') as file:
                content = csv.reader(file, quotechar='"')
                tuits = list(content)
            total_list = total_list  + tuits
    return total_list

def main():
    args = parse_args()
    data = load_all(args)
    already_ids  = [i[0] for i in data]
    #print(already_ids[0], len(already_ids))
    client = tw.Client(bearer_token=token_academic())
    topics = args.topics.split()
    for topic in topics:
        with open('data/initial_collection/tweets_' + 'extended' + '_' + topic + '.csv', 'a') as filehandle:
            linewriter = csv.writer(filehandle, delimiter=',',
                                    quotechar='\"', quoting=csv.QUOTE_ALL)
            queries_count = 0
            for tuit in data:
                #print(tuit[5][21:40])
                if tuit[5][21:40]:
                    if tuit[5][21:40] not in already_ids:
                        try:
                            original_tweet = client.get_tweet(id=tuit[5][21:40],
                                                      tweet_fields=['context_annotations', 'created_at',
                                                                    'conversation_id', 'possibly_sensitive',
                                                                    'referenced_tweets'],
                                                          expansions='author_id')
                        except:
                            continue
                        queries_count += 1
                        if queries_count == 48:
                            print('Sleeping for 15 minutes...')
                            time.sleep(450)
                            queries_count = 0
                        for t in original_tweet:  # THIS IS NOT IDEAL, THE OBJECT RESPONSE SHOULD BE ITERATED DIFFERENTLY
                            if t != None:
                                # print('ANSWERS TO: ', t)
                                if t.context_annotations:
                                    linewriter.writerow(
                                        [t.id, t.text, t.created_at, t.conversation_id, t.possibly_sensitive,
                                         t.referenced_tweets, t.author_id, t.context_annotations[0]['domain']['id'],
                                         t.context_annotations[0]['domain']['name'],
                                         t.context_annotations[0]['entity']['id'],
                                         t.context_annotations[0]['entity']['name']])
                                else:
                                    linewriter.writerow(
                                        [t.id, t.text, t.created_at, t.conversation_id, t.possibly_sensitive,
                                         t.referenced_tweets, t.author_id])
                            break

if __name__ == '__main__':
    main()