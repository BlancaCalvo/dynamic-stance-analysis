# Data Annotation

Compute the reports from the annotation process:

```
python eval/compute_report.py --data ../data/annotated/dynamic_stance_tweeter.csv --task 5 > reports/t5_final_report.csv

python eval/compute_report.py --data ../data/annotated/static_stance_tweeter.csv --task 6 > reports/t6_final_report.csv
```