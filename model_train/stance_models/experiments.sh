
sh use_env.sh

# simple splits with the shuffled topic
sbatch train_model.sh "simple_splits"

# split by topic, train with 4 test with the other topic
for TOPIC in 'vaccines' 'lloguer' 'aeroport'  'subrogada' 'benidormfest'
do
    sbatch train_model.sh "topic_splits/"$TOPIC
    echo $TOPIC
done

sbatch train_model.sh "raco_augment"

for TOPIC in 'vaccines' 'lloguer' 'aeroport'  'subrogada' 'benidormfest'
do
     echo $TOPIC
     sbatch train_model.sh "raco_augment/topic_splits/"$TOPIC
done