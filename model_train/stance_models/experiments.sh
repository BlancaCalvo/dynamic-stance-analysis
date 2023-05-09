
sh use_env.sh

MODEL=$1

# simple splits with the shuffled topic
sbatch train_model.sh "simple_splits" $MODEL

# split by topic, train with 4 test with the other topic
for TOPIC in 'vaccines' 'lloguer' 'aeroport'  'subrogada' 'benidormfest'
do
    sbatch train_model.sh "topic_splits/"$TOPIC $MODEL
    echo $TOPIC
done

# augment the data with raco
sbatch train_model.sh "raco_augment" $MODEL

for TOPIC in 'vaccines' 'lloguer' 'aeroport'  'subrogada' 'benidormfest'
do
     echo $TOPIC
     sbatch train_model.sh "raco_augment/topic_splits/"$TOPIC $MODEL
done

# augment the data but just the easy one
sbatch train_model.sh "filtered_raco_augment" $MODEL