from dataclasses import asdict
from typing import List
import spacy
import json
from datetime import datetime
from pathlib import Path
from spacy.tokens import DocBin
from sentence_transformers import SentenceTransformer, util
from config import Config
from sklearn.model_selection import train_test_split

class SpacyProcessor():

    def __init__(self, config: Config):
        self.data_dir = Path(config.data_dir)
        self.anon_dir = self.data_dir.joinpath("manual")
        self.nlp = spacy.load('en_core_web_lg')
        # self.nlp = spacy.blank("en")
        self.doc_bin = DocBin()
        # self.st_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.raw_data = self.load_data()

    def load_data(self) -> List:
        contracts = []
        for json_file in self.anon_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as file:
                contracts.extend(json.load(file))
        return contracts
    
    def convert_data(self, data: List):
        """
        Convert data to spacy format.
        """
        spacy_folder = self.data_dir.joinpath("spacy")

        for idx, contract in enumerate(data):
            print(f"{idx+1}/{len(data)}")
            ents = []
            doc = self.nlp(contract["text"])
            for entity in contract["entities"]:
                span = doc.char_span(start_idx=entity["start"],
                                     end_idx=entity["end"],
                                     label=entity["type"])
                if span != None:
                    ents.append(span)
            doc.ents = ents
            self.doc_bin.add(doc)
            self.doc_bin.to_disk(spacy_folder.joinpath("dataset.spacy"))

sp = SpacyProcessor(Config())
sp.convert_data(sp.raw_data)
docs = list(sp.doc_bin.get_docs(sp.nlp.vocab))
train_docs, test_docs = train_test_split(docs, test_size=0.3, random_state=42)
train_db = DocBin(docs=train_docs, store_user_data=True)
train_db.to_disk("data/spacy/train.spacy")
test_db = DocBin(docs=test_docs, store_user_data=True)
test_db.to_disk("data/spacy/test.spacy")