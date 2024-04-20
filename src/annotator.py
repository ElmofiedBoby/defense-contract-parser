from dataclasses import asdict
from datetime import datetime
import json
import os
from pathlib import Path
from typing import List
from config import Config
from scraper import Scraper
from model import Precontract, Contract
from openai import OpenAI

class Annotator:

    key = Config.key
    prompt = Config.prompt
    client = OpenAI()
    base_data_filename = Path(Config.data_dir)

    def annotate_contract_safe(self, contract: Precontract) -> str:
        annotated = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            max_tokens=250,  # Adjust based on how long you expect the response to be
            temperature=0.5,  # Adjust for creativity. Lower is more deterministic.
            messages=[
                {
                    "role": "system",
                    "content": f"{self.prompt}",
                },
                {
                    "role": "user",
                    "content": f"\"{contract.contract_text}\""
                }
            ]
        )
        filename = f"{contract.contract_date.strftime('%Y-%m-%d')}_{contract.source_url[56:-1]}.json"
        return (filename, annotated.choices[0].message.content)

    def annotate_contract(self, contract: Precontract) -> Contract:
        annotated = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            max_tokens=250,  # Adjust based on how long you expect the response to be
            temperature=0.5,  # Adjust for creativity. Lower is more deterministic.
            messages=[
                {
                    "role": "system",
                    "content": f"{self.prompt}",
                },
                {
                    "role": "user",
                    "content": f"\"{contract.contract_text}\""
                }
            ]
        )
        
        annotated = json.loads(annotated.choices[0].message.content)
        new_contract = Contract(
            contract_id = annotated['contract_id'],
            federal_agency = annotated['federal_agency'],
            military_branch = contract.military_branch,
            contract_amount = annotated['contract_amount'],
            company_name = annotated['company_name'],
            location = annotated['location'],
            contract_description = annotated['contract_description'],
            estimated_completion_date = annotated['estimated_completion_date'],
            funds_obligated = annotated['funds_obligated'],
            source_url = contract.source_url,
            contract_date = contract.contract_date
        )
        return new_contract
    
    def write_contracts_safe(self, strings):
        if not strings:
            return
        filepath = self.base_data_filename.joinpath("blackbox").joinpath(strings[0][0])
        with open(filepath, 'w') as file:
            for _, second_element in strings:
                second_element = " ".join(line.strip() for line in second_element.splitlines())
                file.write(second_element + '\n')



    def write_contracts(self, contracts: List[Contract]):
        """
        Input: An processed contract (Contract)
        Output: None
        This takes a Contract and writes it to json
        File Format: data/2024-04-19_3749216.json
        """
        if not contracts:
            return  # If the list is empty, do nothing
        
        # Convert all contract objects to dictionaries
        contract_dicts = [asdict(contract) for contract in contracts]

        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)
        filepath = self.base_data_filename.joinpath("annotated").joinpath(f"{contracts[0].contract_date.strftime('%Y-%m-%d')}_{contracts[0].source_url[56:-1]}.json")
        
        # Write the updated data back to the file
        with open(filepath, 'w') as file:
            json.dump(contract_dicts, file, cls=DateTimeEncoder, indent=4)

    def annotate_all(self):
        annotator=Annotator()
        scraper=Scraper()
        files = os.listdir("data/clean")
        for file in files:
            if file.startswith("."):
                continue
            print(f"File: {file}")
            contracts = scraper.read_precontract(filename=f"data/clean/{file}")
            annotations = []
            for contract in contracts:
                print(f"Contract: {contract.source_url}")
                annotations.append(annotator.annotate_contract(contract))
            annotator.write_contracts(annotations)

    def annotate_all_safe(self):
        annotator=Annotator()
        scraper=Scraper()
        files = os.listdir("data/clean")
        for file in files:
            if file.startswith("."):
                continue
            print(f"File: {file}")
            contracts = scraper.read_precontract(filename=f"data/clean/{file}")
            annotations = []
            for contract in contracts:
                print(f"Contract: {contract.source_url}")
                annotations.append(annotator.annotate_contract_safe(contract))
            annotator.write_contracts_safe(annotations)

annotator = Annotator()
annotator.annotate_all_safe()