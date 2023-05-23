# Loading script for the ReviewsFinder dataset.


import json
import csv

import datasets


logger = datasets.logging.get_logger(__name__)


_CITATION = """ """


_DESCRIPTION = """ Static Stance """


_HOMEPAGE = """ """



_URL = ""
_TRAINING_FILE = "train.jsonl"
_DEV_FILE = "dev.jsonl"
_TEST_FILE = "test.jsonl"


class StaticStanceConfig(datasets.BuilderConfig):
    """ Builder config for the DynamicStance dataset """

    def __init__(self, **kwargs):
        """BuilderConfig for DynamicStance.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(StaticStanceConfig, self).__init__(**kwargs)


class StaticStance(datasets.GeneratorBasedBuilder):
    """ StaticStance Dataset """


    BUILDER_CONFIGS = [
        StaticStanceConfig(
            name="StaticStance",
            version=datasets.Version("1.0.0"),
            description="StaticStance dataset",
        ),
    ]


    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "label": datasets.features.ClassLabel
                    (names=
                        [
                            "FAVOUR",
                            "AGAINST",
                            "NEUTRAL",
                            "NA"
                        ]
                    ),
                }
            ),
            homepage=_HOMEPAGE,
            citation=_CITATION,
        )

                
    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        urls_to_download = {
            "train": f"{_URL}{_TRAINING_FILE}",
            "dev": f"{_URL}{_DEV_FILE}",
            "test": f"{_URL}{_TEST_FILE}",
        }
        downloaded_files = dl_manager.download_and_extract(urls_to_download)

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": downloaded_files["train"]}),
            datasets.SplitGenerator(name=datasets.Split.VALIDATION, gen_kwargs={"filepath": downloaded_files["dev"]}),
            datasets.SplitGenerator(name=datasets.Split.TEST, gen_kwargs={"filepath": downloaded_files["test"]}),
        ]


    def _generate_examples(self, filepath):
        """This function returns the examples in the raw (text) form."""
        logger.info("generating examples from = %s", filepath)
        with open(filepath, encoding="utf-8") as f:
            data = [json.loads(line) for line in f]
            for id_, article in enumerate(data):
                    yield id_, {
                        "text": article['text'],
                        "label": article['label'],
                    }
