
### Model Training

```
python model_train/$MODEL_FOLDER/splits_generate.py # stance_models static_stance crosslingual_vaccines

cd model_train/$MODEL_FOLDER/
sh experiments.sh "roberta-large-ca-v2" # not for cosslingual
sh experiments.sh "mdeberta-v3-base"
```

# Test in Dutch for crosslingual

Change test file in dataloader.

```
sh test_nl.sh "cat_nl" $CHECKPOINT
```