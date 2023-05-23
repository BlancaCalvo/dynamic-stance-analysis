
for FOLDER in 'cat_only' 'cat_nl'
do
    echo $FOLDER
    scp data/crosslingual_vaccines/$FOLDER/* dt:/gpfs/scratch/bsc88/bsc88080/crosslingual_vaccines/data/$FOLDER/
done
