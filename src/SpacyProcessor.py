from dataclasses import asdict
from typing import List
import spacy
import json
from datetime import datetime
from pathlib import Path
from spacy.tokens import DocBin
from sentence_transformers import SentenceTransformer, util
from config import Config

class SpacyProcessor():

    def __init__(self, config: Config):
        self.data_dir = Path(config.data_dir)
        self.anon_dir = self.data_dir.joinpath("annotated")
        self.nlp = spacy.load('en_core_web_lg')
        # self.nlp = spacy.blank("en")
        self.doc_bin = DocBin()
        self.st_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.raw_data = self.load_data()

    def load_data(self) -> List:
        contracts = []
        for json_file in self.data_dir.joinpath("annotated").glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as file:
                contracts.extend(json.load(file))
        return contracts
    
    def convert_data(self, data: List):
        """
        Convert data to spacy format.
        """
        spacy_folder = self.data_dir.joinpath("spacy")

        def correct_contract_amount(amount: float) -> str:
            formatted_value = "{:,.0f}".format(amount) if amount.is_integer() else "{:,.2f}".format(amount).rstrip('0').rstrip('.')
            return "$" + formatted_value
        
        def correct_time(date_str: str) -> str:
            if 'T' in date_str:
                date_format = '%Y-%m-%dT%H:%M:%S'
            else:
                date_format = '%Y-%m-%d'
            date_obj = datetime.strptime(date_str, date_format)
            formatted_date_str = date_obj.strftime('%B %d, %Y')
            return formatted_date_str

        def find_context(contract_text: str, contract_ent: str, padding: int) -> tuple[int, int]:
            sentences = contract_text.split('. ')
            ent_embedding = self.st_model.encode(contract_ent, convert_to_tensor=True)
            sentence_embeddings = self.st_model.encode(sentences, convert_to_tensor=True)
            cosine_scores = util.pytorch_cos_sim(ent_embedding, sentence_embeddings)
            highest_score_index = cosine_scores.argmax()
            start_index = contract_text.find(sentences[highest_score_index])
            end_index = start_index + len(sentences[highest_score_index])
            start_index = max(0, start_index - padding)
            end_index = min(len(contract_text), end_index + padding)
            return start_index, end_index
                
        def generate_ents(keys: dict) -> List[tuple]:
            allowed_keys = [
                "contract_id",
                "federal_agency",
                "contract_amount",
                "company_name",
                "location",
                "contract_description",
                "estimated_completion_date",
                "funds_obligated"
            ]
            ents = []

            for k in keys.keys():
                if k not in allowed_keys:
                    continue
                if k == "contract_amount":
                    keys[k] = correct_contract_amount(keys[k])
                if k == "estimated_completion_date":
                    keys[k] = correct_time(keys[k])
                start = keys["contract_text"].find(keys[k])
                if start == -1:
                    if k == "contract_description":
                        start, end = find_context(keys["contract_text"], keys[k], padding=20)
                    else:
                        start, end = find_context(keys["contract_text"], keys[k], padding=0)
                else:
                    end = start + len(k)
                key = k.upper()
                ents.append((start, end, key))

            return ents

        for idx, contract in enumerate(data):
            print(f"{idx+1}/{len(data)}")
            doc = self.nlp(contract["contract_text"])
            raw_ents = generate_ents(contract)
            ents = []
            for start, end, key in raw_ents:
                span = doc.char_span(start_idx=start, end_idx=end, label=key, alignment_mode="expand")
                ents.append(span)
            doc.ents = ents
            self.doc_bin.add(doc)
            if idx+1 % 10 == 0:
                self.doc_bin.to_disk(spacy_folder.joinpath("train.spacy"))

sp = SpacyProcessor(Config())
sp.convert_data(sp.raw_data)