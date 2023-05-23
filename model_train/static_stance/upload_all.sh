
for FOLDER in 'simple_splits'
do
    echo $FOLDER
    scp data/static_data/$FOLDER/*.jsonl dt:/gpfs/scratch/bsc88/bsc88080/static_stance/data/$FOLDER/
    scp model_train/static_stance/StaticStance.py dt:/gpfs/scratch/bsc88/bsc88080/static_stance/data/$FOLDER/
done

for TOPIC in 'vaccines' 'lloguer' 'aeroport'  'subrogada' 'benidormfest'
do
     echo $TOPIC
     scp data/static_data/topic_splits/$TOPIC/*.jsonl dt:/gpfs/scratch/bsc88/bsc88080/static_stance/data/topic_splits/$TOPIC/
     scp model_train/static_stance/StaticStance.py dt:/gpfs/scratch/bsc88/bsc88080/static_stance/data/topic_splits/$TOPIC/
done
