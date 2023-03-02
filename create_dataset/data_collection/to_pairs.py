import csv
import argparse
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", default='vaccines', type=str, required=False)
    parser.add_argument("--directory", default='data/initial_collection/', type=str, required=False)
    parser.add_argument("--out_directory", default='data/', type=str, required=False)
    args = parser.parse_args()
    print(args)
    # for all csvs in the folder, do this and put it in a single file
    counter = 0
    counter_answers = 0
    for topic in args.topics.split(' '):
        no_answer_tweets = []
        for f in glob.glob(args.directory+'tweets_*_'+topic+'.csv'):
            with open(f, 'r') as file:
                content = csv.reader(file, quotechar='"')
                tuits = list(content)

            with open(args.out_directory+'paired_tweets_'+topic+'.csv', 'a', newline='') as output_file:
                linewriter = csv.writer(output_file, delimiter=',',
                                        quotechar='\"', quoting=csv.QUOTE_ALL, lineterminator='\n')
                answers = tuits
                for tuit in tuits:
                    counter += 1
                    for answers_to in answers:
                        if tuit[5][21:40] == answers_to[0]:
                            counter_answers += 1
                            linewriter.writerow([answers_to[0], tuit[0], answers_to[1].replace('\n', '. '), tuit[1].replace('\n', '. '), tuit[2], answers_to[2], tuit[3], answers_to[6], tuit[6]])
                            break
                    if tuit[5] == '':
                        no_answer_tweets.append([tuit[0], tuit[1].replace('\n', '. '), tuit[2], tuit[3]])
                        #no_answer_tweets.append(tuit[3])

        with open(args.out_directory+'no_answer_'+topic+'.csv', 'w') as myfile:
            #for cid in no_answer_tweets:
            #    myfile.write(cid+'\n')
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            for line in no_answer_tweets:
                wr.writerow(line)

    print(counter)
    print(counter_answers)

if __name__ == '__main__':
    main()