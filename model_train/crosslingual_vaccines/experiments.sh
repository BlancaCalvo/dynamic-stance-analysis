
sh use_env.sh

MODEL=$1

sbatch train_model.sh "cat_only" $MODEL

sbatch train_model.sh "cat_nl" $MODEL