# Dynamic-Stance

Download the different corpora: 

```
python download_strategy.py --topic vaccines --academic_credentials --end_date 2021-01-03T00:00:00Z --query_strategy yearly_2021

python download_strategy.py --topic lloguer --academic_credentials

python download_strategy.py --topic subrogada --academic_credentials

python download_strategy.py --topic aeroport --academic_credentials

python download_strategy.py --topic benidormfest --academic_credentials  --query_strategy sequential --end_date 2022-02-15T00:00:00Z --start_date 2022-01-29T22:00:00Z --amount 5000

python extend_download.py --topics 'vaccines lloguer aeroport subrogada benidormfest'
```


```
python to_pairs.py --topics 'vaccines lloguer aeroport subrogada benidormfest'

python to_final.py --topics 'vaccines lloguer aeroport subrogada benidormfest'
```

Extend the corpus:

```
python download_strategy.py --topic lloguer --academic_credentials --amount 2000 --query_strategy sequential --start_date '2022-03-27T00:00:00Z' --end_date '2023-01-23T00:00:00Z' --out_directory data/ampliation/

python download_strategy.py --topic subrogada --academic_credentials --amount 2000 --query_strategy sequential --start_date '2022-03-27T00:00:00Z' --end_date '2023-01-23T00:00:00Z' --out_directory data/ampliation/

python to_pairs.py --topics 'lloguer subrogada' --directory data/ampliation/ --out_directory data/ampliation/

python to_final.py --topics 'lloguer subrogada' --directory data/ampliation/
```
