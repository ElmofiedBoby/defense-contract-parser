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
    date_format = Config.date_format

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
        with open(filepath, 'w', encoding='utf-8') as file:
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

    def write_safe_annotations(self, start_file: str, end_file: str, skip=True):

        def write_safe_annotation_list(contracts: List[Contract]):
            contracts_dict = [asdict(contract) for contract in contracts]
            if contracts:
                class DateTimeEncoder(json.JSONEncoder):
                    def default(self, o):
                        if isinstance(o, datetime):
                            return o.isoformat()
                        return super().default(o)
                filepath = self.base_data_filename.joinpath("annotated").joinpath(f"{contracts[0].contract_date.strftime('%Y-%m-%d')}_{contracts[0].source_url[56:-1]}.json")
                with open(filepath, 'w') as file:
                    json.dump(contracts_dict, file, cls=DateTimeEncoder, indent=4)

        for file in os.listdir("data/clean"):
            if file.startswith("."):
                continue
            if file != start_file and skip==True:
                continue
            elif file == start_file:
                skip = False
            if file == end_file:
                break
            contracts = self.clean_safe_annotation(file)
            write_safe_annotation_list(contracts)

    def clean_safe_annotation(self, filename: str) -> List[Contract]:
        """
        We need to append additional data from the Precontract object.

        Safe annotations are just saved to a single line, regardless of JSON validity.
        We also need to check each line for two things:
        1. JSON Validity
        2. All fields are present, are of the right type, and have relevant data.
        """
        def parse_money(raw_money: str) -> float:
            try:
                money = float(raw_money.replace('$', '').replace(',', ''))
            except ValueError:
                print("Error: The string does not contain a valid number")
                return None
            return money

        def parse_date(raw_date: str) -> datetime:
            date_text = raw_date.split(" ")
            if "Jan" in date_text[0]:
                date_text[0] = "January"
            elif "Feb" in date_text[0]:
                date_text[0] = "February"
            elif "Mar" in date_text[0]:
                date_text[0] = "March"
            elif "Apr" in date_text[0]:
                date_text[0] = "April"
            elif "Jun" in date_text[0]:
                date_text[0] = "June"
            elif "Jul" in date_text[0]:
                date_text[0] = "July"
            elif "Aug" in date_text[0]:
                date_text[0] = "August"
            elif "Sep" in date_text[0]:
                date_text[0] = "September"
            elif "Oct" in date_text[0]:
                date_text[0] = "October"
            elif "Nov" in date_text[0]:
                date_text[0] = "November"
            elif "Dec" in date_text[0]:
                date_text[0] = "December"
            if len(date_text) == 3:
                # Month Day, Year
                if not "," in date_text[1]:
                    date_text[1] = f"{date_text[1]},"
                try:
                    date = datetime.strptime(f"{date_text[0]} {date_text[1]} {date_text[2]}", self.date_format)
                    return date
                except ValueError as e:
                    return None
            elif len(date_text) == 2:
                # Month, Year
                try:
                    date = datetime.strptime(f"{date_text[0]} {date_text[1]} 1", "%B %Y %d")
                    return date
                except ValueError as e:
                    return None
            else:
                return None
        
        def read_specific_line(filepath: str, line_number: int) -> str:
            try:
                with open(filepath, 'r', encoding="utf-8", errors="ignore") as file:
                    lines = file.readlines()
                    return lines[line_number - 1].strip()
            except Exception as e:
                print(filepath)
                raise e
        
        def verify_contract_fields(raw_data: str) -> bool:
            def find_banned_words(raw_data: str, log=False) -> bool:
                """
                Returns true if banned word is found
                """
                banned_words = [
                    "To be determined",
                    "Not specified",
                    "Not provided",
                    "n/a",
                    "Not applicable",
                    "N/a",
                    "n/A",
                    "N/A",
                    "No completion date"
                ]
                for word in banned_words:
                    if word in raw_data:
                        if log:
                            print(word)
                        return True
                if raw_data == "":
                    return True
                else:
                    return False
            # Check 1: Does it parse?
            try:
                json_data = json.loads(raw_data)
            except Exception:
                # print("Unable to parse.")
                return False

            # Check 2: Are all fields present?
            valid_fields = [
                            "contract_id",
                            "federal_agency",
                            "contract_amount",
                            "company_name",
                            "location",
                            "contract_description",
                            "estimated_completion_date",
                            "funds_obligated"
                            ]
            if set(valid_fields) != set(json_data.keys()):
                # print(f"Missing fields {set(valid_fields).symmetric_difference(set(json_data.keys()))}")
                return False

            # Check 3: Are all fields valid types?
            if type(json_data["contract_id"]) != type("") or len(json_data["contract_id"]) < 13:
                print("contract_id error: " +str(json_data["contract_id"]))
                return False
            if type(json_data["federal_agency"]) != type("") or find_banned_words(json_data["federal_agency"]):
                print("federal_agency error")
                return False
            if type(json_data["contract_amount"]) != type("") or not '$' in json_data["contract_amount"] or find_banned_words(json_data["contract_amount"]):
                print("contract_amount error")
                return False
            if type(json_data["company_name"]) != type("") or find_banned_words(json_data["company_name"]):
                print("company_name error")
                return False
            if type(json_data["location"]) != type("") or find_banned_words(json_data["location"]):
                print("location error")
                return False
            if type(json_data["contract_description"]) != type("") or find_banned_words(json_data["contract_description"]):
                print("contract_description error")
                return False
            if type(json_data["estimated_completion_date"]) != type("") or find_banned_words(json_data["estimated_completion_date"]) or parse_date(json_data["estimated_completion_date"]) is None:
                print("estimated_completion_date error: "+ str(json_data["estimated_completion_date"]))
                return False
            if type(json_data["funds_obligated"]) != type("") or find_banned_words(json_data["funds_obligated"]):
                print("funds_obligated error")
                return False
            
            return True
        
        scraper = Scraper()
        contracts = []
        precontracts = scraper.read_precontract(filename=f"data/clean/{filename}")
        for idx, contract in enumerate(precontracts):
            annotated_raw = read_specific_line(f"data/blackbox/{filename}", idx+1)
            # print(verify_contract_fields(annotated_raw))
            if verify_contract_fields(annotated_raw):
                json_data = json.loads(annotated_raw)
                contracts.append(
                    Contract(
                        contract_id = json_data["contract_id"],
                        federal_agency = json_data["federal_agency"],
                        military_branch = contract.military_branch,
                        contract_amount = parse_money(json_data["contract_amount"]),
                        contract_date = contract.contract_date,
                        company_name = json_data["company_name"],
                        location = json_data["location"],
                        contract_description = json_data["contract_description"],
                        estimated_completion_date = parse_date(json_data["estimated_completion_date"]),
                        funds_obligated = json_data["funds_obligated"],
                        source_url = contract.source_url,
                        contract_text = contract.contract_text
                    )
                )
        return contracts


    def annotate_all_safe(self, start_file: str, skip: bool):
        annotator=Annotator()
        scraper=Scraper()
        files = os.listdir("data/clean")
        for file in files:
            if file.startswith("."):
                continue
            if file != start_file and skip==True:
                continue
            elif file == start_file:
                skip = False
            print(f"File: {file}")
            contracts = scraper.read_precontract(filename=f"data/clean/{file}")
            annotations = []
            for contract in contracts:
                annotations.append(annotator.annotate_contract_safe(contract))
            annotator.write_contracts_safe(annotations)

annotator = Annotator()
# annotator.annotate_all_safe("2015-09-14_617124.json", True)
# annotator.write_safe_annotations("2014-07-03_605970.json", "2017-09-05_1299955.json", True)