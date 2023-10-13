# Dynamic Stance

This is the repository for the article "Dynamic Stance: Modeling Discussions by Labeling the Interactions". 

Stance detection is an increasingly popular task that has been mainly modeled as a static task, by assigning the expressed attitude of a text toward a given topic. Such a framing presents limitations, with trained systems showing poor generalization capabilities and being strongly topic-dependent. In this work, we propose modeling stance as a dynamic task, by focusing on the interactions between a message and their replies. For this purpose, we present a new annotation scheme that enables the categorization of all kinds of textual interactions. As a result, we have created a new corpus, the Dynamic Stance Corpus (DySC), consisting of three datasets in two middle-resourced languages: Catalan and Dutch. Our data analysis further supports our modeling decisions, empirically showing differences between the annotation of stance in static and dynamic contexts. We fine-tuned a series of monolingual and multilingual models on DySC, showing portability across topics and languages.

The folders of [analysis](https://github.com/projecte-aina/dynamic-stance-analysis/tree/main/analysis) and [create_dataset](https://github.com/projecte-aina/dynamic-stance-analysis/tree/main/create_dataset) contain the scripts used to create and analyse the datasets of this article. If you want to reproduce the results follow the instructions in [model_train](https://github.com/projecte-aina/dynamic-stance-analysis/tree/main/model_train). 

### Cite
