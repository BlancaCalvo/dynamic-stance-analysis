
import tweepy as tw
import csv
import argparse
from twitter_credentials import credentials, token_mine, token_academic
import datetime
import time

def parsing_arguments(parser):
    parser.add_argument("--academic_credentials", action='store_true')
    parser.add_argument("--token", type=str, required=False)
    parser.add_argument("--amount", type=int, required=False)
    parser.add_argument("--topic", default='vaccines', type=str, required=True)
    parser.add_argument("--end_date", default='2021-01-03T00:00:00Z', type=str,
                        help='it should look like 2021-12-31T00:00:00Z', required=False)
    parser.add_argument("--start_date", default='2021-01-03T00:00:00Z', type=str,
                        help='it should look like 2021-12-31T00:00:00Z', required=False)
    parser.add_argument("--query_strategy", default=None, type=str, required=False, help='Options: yearly_2021, one_date, sequential')
    parser.add_argument("--out_directory", default='data/initial_collection/', type=str, required=False)
    return parser

class TopicWithNoQuery(Exception):
    def __init__(self):
        super().__init__('No query for this topic yet.')

# class NoToken(Exception):
#     def __init__(self):
#         super().__init__('Please write your token.')

def choose_query(topic):
    if topic == "vaccines":
        query = 'lang:ca -is:retweet -has:images (vacunes OR vacuna OR vaccí OR vaccines  \
                OR pfizer OR astrazeneca OR vacuna moderna OR passaport covid \
                OR tercera dosis OR efectes secundaris OR dosi reforç OR vacunats OR vacunades  \
                OR tercera dosis OR vacuneu-vos OR vacunem-nos OR vacunet OR vacune\'t OR vaccinat)'
        return query
    elif topic == "aeroport":
        query = 'lang:ca -is:retweet -has:images (ampliació aeroport OR #noampliacioaeroport OR ambiental aeroport \
                OR 19S OR aeroport delta OR aeroport el prat OR sostenible aeroport \
                 OR més verd del món OR delta llobregat OR soroll avions OR aeroport internacional OR ricarda) -kabul'
                # hub intercontinental
        return query
    elif topic == "subrogada":
        query = "lang:ca -is:retweet -has:images (gestació subrogada OR ventre de lloguer OR mares portadores \
                OR explotació reproductiva OR inscripció de menors OR  dona gestant \
                 OR #gestaciosubrogada OR maternitat subrogada OR paternitat subrogada OR ventres de lloguer \
                 OR embaràs subrogat OR inscripció de nens OR mare gestant OR comprar bebes OR comprar bebès OR \
                 comprar nens OR comprar criatures)" # després filtrar perquè comprar i criatures vagi seguit
                    #gestacionsustituta "la gestant" explotació reproductiva
        return query
    elif topic == "lloguer":
        query = 'lang:ca -is:retweet -has:images (regulació lloguer OR preus de lloguer OR #regularlloguers \
                OR regulació dels preus OR okupes OR immobiliari OR  #RegulemElsLloguersJA OR llei de vivenda \
                 OR desnonaments OR desnonament OR fons voltor OR fons voltors OR blackstone OR \
                seguretat als propietaris OR propietaris immobiliaris OR lobbies immobiliaris)'
        return query
    elif topic == "benidormfest":
        query = 'lang:ca -is:retweet -has:images (benidorm fest OR tanxungueiras OR chanel OR rigoberta OR ay mama OR \
                hai fronteiras OR slomo OR rtve jurat OR eurovisión OR tongo)'
        return query
    else:
        raise TopicWithNoQuery

def get_end_dates(end_date):
    queries = [end_date]
    date_time_obj = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
    for i in range(50):
        date_time_obj += datetime.timedelta(days=7)
        string = date_time_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        queries.append(string)
    return queries

def choose_strategy(args):
    if args.query_strategy == 'yearly_2021':
        queries = get_end_dates(args.end_date)
    elif args.query_strategy == 'one_date':
        queries = [args.end_date]
    elif args.query_strategy == 'sequential':
        queries = [args.start_date, args.end_date]
    elif args.topic == 'subrogada':
        queries = ['2020-07-29T00:00:00Z', '2020-08-05T00:00:00Z', '2017-08-01T00:00:00Z', '2017-08-08T00:00:00Z', '2017-01-30T00:00:00Z', '2017-02-06T00:00:00Z', '2019-02-04T00:00:00Z', '2019-02-11T00:00:00Z', '2019-02-18T00:00:00Z', '2019-02-25T00:00:00Z', '2019-03-04T00:00:00Z', '2019-04-10T00:00:00Z', '2019-04-17T00:00:00Z', '2019-04-24T00:00:00Z', '2019-08-14T00:00:00Z', '2019-08-21T00:00:00Z', '2022-02-26T00:00:00Z', '2022-03-02T00:00:00Z', '2022-03-09T00:00:00Z', '2022-03-16T00:00:00Z', '2022-03-13T00:00:00Z', '2022-03-20T00:00:00Z', '2022-03-27T00:00:00Z']
    elif args.topic == 'lloguer':
        queries = ['2020-08-01T00:00:00Z', '2020-08-08T00:00:00Z', '2020-08-15T00:00:00Z', '2020-08-22T00:00:00Z', '2020-08-29T00:00:00Z', '2020-09-01T00:00:00Z', '2020-09-08T00:00:00Z', '2020-09-15T00:00:00Z', '2020-09-22T00:00:00Z', '2020-09-29T00:00:00Z', '2021-09-01T00:00:00Z', '2021-09-08T00:00:00Z', '2021-09-15T00:00:00Z', '2021-09-22T00:00:00Z', '2021-09-29T00:00:00Z', '2021-10-01T00:00:00Z', '2021-10-08T00:00:00Z', '2021-10-15T00:00:00Z', '2021-10-22T00:00:00Z', '2021-10-29T00:00:00Z']
    elif args.topic == 'aeroport':
        queries = ['2021-07-01T00:00:00Z', '2021-07-08T00:00:00Z', '2021-07-15T00:00:00Z', '2021-07-22T00:00:00Z', '2021-09-29T00:00:00Z','2021-08-01T00:00:00Z', '2021-08-08T00:00:00Z', '2021-08-15T00:00:00Z', '2021-08-22T00:00:00Z', '2021-08-29T00:00:00Z','2021-09-01T00:00:00Z', '2021-09-08T00:00:00Z', '2021-09-15T00:00:00Z', '2021-09-22T00:00:00Z', '2021-09-29T00:00:00Z', '2021-10-01T00:00:00Z', '2021-10-08T00:00:00Z', '2021-10-15T00:00:00Z', '2021-10-22T00:00:00Z', '2021-10-29T00:00:00Z', '2021-11-01T00:00:00Z', '2021-11-08T00:00:00Z', '2021-11-15T00:00:00Z', '2021-11-22T00:00:00Z', '2021-11-29T00:00:00Z']
    else:
        print('No time strategy defined.')
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        string = yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')
        queries = [string]
    return queries

def issue_with_subrogada(text):
    # I need to add this filter because the tweeter API does not take into account the order of the keywords and "comprar nens" matches a lot of stuff
    list_strings = ['gestació subrogada', 'ventre de lloguer', 'mares portadores', 'explotació reproductiva',
                    'inscripció de menors', 'dona gestant', '#gestaciosubrogada', 'maternitat subrogada',
                    'paternitat subrogada', 'ventres de lloguer', '#gestaciósubrogada',
                    'embaràs subrogat', 'inscripció de nens', 'mare gestant', 'comprar bebes', 'comprar bebès',
                    'comprar bebés', 'comprar nens', 'comprar criatures', '"compra" ni "ven" cap infant', 'pares biològics',
                    'filiar un nadó']
                    #, 'persona gestant', 'lloguer de ventres', 'gestacio subrogada', 'explotació sexual i reproductiva',
                    # 'explotació sexual ni reproductiva', "comprar un nen", "gestació subrrogada", "compra nens"]
    word_in_tuit = False
    for word in list_strings:
        if word in text.lower():
            word_in_tuit = True
    return word_in_tuit

def academic_query(client, query, end_time, args, start_time=None, limit=100):
    queries_count = 0
    with open(args.out_directory+'tweets_'+end_time[:13]+'_'+args.topic+'.csv', 'a') as filehandle:
        linewriter = csv.writer(filehandle, delimiter=',',
                                quotechar='\"', quoting=csv.QUOTE_ALL)

        for i, tweet in enumerate(tw.Paginator(client.search_all_tweets, query=query,
                                          tweet_fields=['context_annotations', 'created_at', 'conversation_id',
                                                        'possibly_sensitive', 'referenced_tweets', 'author_id'],
                                          max_results=100,
                                          end_time=end_time,
                                          start_time=start_time,
                                          expansions='author_id').flatten(limit=limit)):

            continue_sub = True
            if args.topic == 'subrogada':
                continue_sub = issue_with_subrogada(tweet.text)

            if tweet.context_annotations and continue_sub:
                linewriter.writerow(
                    [tweet.id, tweet.text, tweet.created_at, tweet.conversation_id, tweet.possibly_sensitive,
                     tweet.referenced_tweets, tweet.author_id, tweet.context_annotations[0]['domain']['id'],
                     tweet.context_annotations[0]['domain']['name'],
                     tweet.context_annotations[0]['entity']['id'],
                     tweet.context_annotations[0]['entity']['name']])
            elif continue_sub:
                linewriter.writerow(
                    [tweet.id, tweet.text, tweet.created_at, tweet.conversation_id, tweet.possibly_sensitive,
                     tweet.referenced_tweets, tweet.author_id])
            #else:
            #    print(tweet)
            queries_count += 1
            if queries_count == 48:
                print('Sleeping for 15 minutes...')
                time.sleep(450)
                queries_count = 0

            # print(tweet.referenced_tweets) # REPLY_TO O QUOTED: A list of Tweets this Tweet refers to. For example, if the parent Tweet is a Retweet, a Retweet with comment (also known as Quoted Tweet) or a Reply, it will include the related Tweet referenced to by its parent.
            # print(tweet.conversation_id) # ORIGINAL CONTEXT: The Tweet ID of the original Tweet of the conversation (which includes direct replies, replies of replies).
            if tweet.referenced_tweets and continue_sub:
                for original in tweet.referenced_tweets:
                    original_tweet = client.get_tweet(id=original.id,
                                                      tweet_fields=['context_annotations', 'created_at',
                                                                    'conversation_id', 'possibly_sensitive',
                                                                    'referenced_tweets', 'author_id'],
                                                      expansions='author_id')
                    queries_count+=1
                    if queries_count == 48:
                        print('Sleeping for 15 minutes...')
                        time.sleep(450)
                        queries_count=0
                    for t in original_tweet:  # THIS IS NOT IDEAL, THE OBJECT RESPONSE SHOULD BE ITERATED DIFFERENTLY
                        if t != None:
                            #print('ANSWERS TO: ', t)
                            if t.context_annotations:
                                linewriter.writerow(
                                    [original.id, t.text, t.created_at, t.conversation_id, t.possibly_sensitive,
                                     t.referenced_tweets, t.author_id, t.context_annotations[0]['domain']['id'],
                                     t.context_annotations[0]['domain']['name'],
                                     t.context_annotations[0]['entity']['id'],
                                     t.context_annotations[0]['entity']['name']])
                            else:
                                linewriter.writerow(
                                    [original.id, t.text, t.created_at, t.conversation_id, t.possibly_sensitive,
                                     t.referenced_tweets, t.author_id])
                        break


def normal_query(api, query, end_time, args):
    with open(args.out_directory+'tweets_ind_'+end_time[:10]+'_'+args.topic+'.csv', 'a', newline='') as csvfile:
        linewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='\"', quoting=csv.QUOTE_ALL)

        for full_tweets in tw.Cursor(api.search_tweets, q=query,
                                     tweet_mode='extended').items(15):
            if full_tweets.in_reply_to_status_id != None:  # if it's an answer, it should look for the original tweet (use while if I want the whole thread)
                answer = full_tweets
                full_tweets = api.get_status(id=full_tweets.in_reply_to_status_id_str, tweet_mode='extended')
                if full_tweets.in_reply_to_status_id == None:
                    linewriter.writerow([full_tweets.id, answer.id, full_tweets.full_text,
                                         answer.full_text])
                    break
            print('Tweet: ', full_tweets.full_text)

            for answer in tw.Cursor(api.search_tweets, q='to:' + full_tweets.user.screen_name, result_type='recent',
                                    tweet_mode='extended').items(5):  # it just looks one level lower
                if hasattr(answer, 'in_reply_to_status_id_str'):
                    if (answer.in_reply_to_status_id_str == full_tweets.id_str):
                        print('Reply: ', answer.full_text)
                        linewriter.writerow([full_tweets.id, answer.id, full_tweets.full_text,
                                             answer.full_text])


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    # load credentials
    if args.academic_credentials:
        client = tw.Client(bearer_token=token_academic())
    else:
        #client = tw.Client(token_mine())
        api = credentials()

    # load search query for the topic
    query = choose_query(args.topic)

    # define query strategies
    queries = choose_strategy(args)

    # Every query wait for 15 minutes
    if args.query_strategy == 'sequential' and args.academic_credentials:
        academic_query(client, query, queries[1], args, queries[0], args.amount)
        #time.sleep(450)
    else:
        for i,q in enumerate(queries):
            if args.academic_credentials:
                academic_query(client, query, q, args)
                #time.sleep(450)
            else:
                normal_query(api, query, q, args) # crec que no funciona amb la query de vaccines

if __name__ == '__main__':
    main()
