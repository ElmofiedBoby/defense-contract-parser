import json
import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime
from typing import List
from model import Precontract
from config import Config
from dataclasses import asdict

class Scraper:

    base_url = Config.base_url
    date_format = Config.date_format
    base_data_filename = Path(Config.data_dir)

    def get_max_pages(self) -> int:
        """
        Input: None
        Return: Max Page (int)
        Returns the maximum available page. This works due to a website design
        flaw - putting in an excessive number reveals the max number.
        """
        # Set to an arbitrarily large number to ensure we reach the last page
        test_url = f"{self.base_url}?Page=1000000000"
        response = requests.get(test_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        return int(soup.find('span', class_='fa-chevron-right').parent.parent.fetchPrevious("div")[0].getText(strip=True))

    def get_date_url(self, page_num: int) -> List[str]:
        """
        Input: Page Number (int)
        Return: List of URLs
        This will take in a page number and return the URLs for each date on a specific page
        """
        response = requests.get(self.base_url+f"?Page={page_num}")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
        return [item.get('article-url') for item in list(soup.find('feature-template').children) if item != "\n"]
        
    def get_date_contract(self, url: str) -> List[Precontract]:
        """
        Input: A date's url (str)
        Return: List of Contracts
        This will take in a url for a specific date and return a list of Precontract objects.
        """
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        date_text_find = soup.find("h1", class_="maintitle")
        if date_text_find is None:
            return None
        date_text = date_text_find.getText(strip=True)[14:].split(" ")

        if date_text[0] == "Jan.":
            date_text[0] = "January"
        elif date_text[0] == "Feb.":
            date_text[0] = "February"
        elif date_text[0] == "Aug.":
            date_text[0] = "August"
        elif date_text[0] == "Sept.":
            date_text[0] = "September"
        elif date_text[0] == "Oct.":
            date_text[0] = "October"
        elif date_text[0] == "Nov.":
            date_text[0] = "November"
        elif date_text[0] == "Dec.":
            date_text[0] = "December"

        date = datetime.strptime(f"{date_text[0]} {date_text[1]} {date_text[2]}", self.date_format)
        contract_data = [item for item in list(list(soup.find("div", class_="ntext").children)[1].children) if item != "\n"]
        contracts = []
        curr_branch = ""
        for contract in contract_data:
            if type(contract) == NavigableString:
                continue
            if type(contract) == Tag:
                if bool(contract.attrs) and not contract.getText().isspace() and contract.getText(strip=True) != "CONTRACTS":
                    curr_branch = contract.text
                    continue
                if len(contract.text) < 100:
                    continue
                contracts.append(
                    Precontract(
                        military_branch=curr_branch,
                        source_url=url,
                        contract_text = contract.text,
                        contract_date = date
                    )
                )
        return contracts
    
    def read_precontract(self, filename: str) -> List[Precontract]:
        with open(filename, 'r') as file:
            data = json.load(file)
            
        precontracts = [
            Precontract(
                military_branch=item['military_branch'],
                source_url=item['source_url'],
                contract_text=item['contract_text'],
                contract_date=datetime.fromisoformat(item['contract_date'])
            )
            for item in data
        ]
        return precontracts

    def write_precontract(self, contract: Precontract):
        """
        Input: An unprocessed contract (Precontract)
        Output: None
        This takes a precontract and writes it to json
        File Format: data/2024-04-19_3749216.json
        """
        contract_dict = asdict(contract)
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)
        filepath = self.base_data_filename.joinpath("raw").joinpath(f"{contract.contract_date.strftime('%Y-%m-%d')}_{contract.source_url[56:-1]}.json")
        # Check if the file already exists
        if filepath.exists():
            # Read the existing data
            with open(filepath, 'r') as file:
                try:
                    data = json.load(file)
                    # Ensure data is in list format
                    if not isinstance(data, list):
                        data = [data]
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        # Append the new contract data
        data.append(contract_dict)
        
        # Write the updated data back to the file
        with open(filepath, 'w') as file:
            json.dump(data, file, cls=DateTimeEncoder, indent=4)

    def download_all_contracts(self, start_page: int):
        """
        Input: None
        Output: None
        This downloads all available contracts.
        """
        for i in range(start_page, self.get_max_pages()):
            print(f"Page {i+1}")
            urls = self.get_date_url(i)
            for w in urls:
                contracts = self.get_date_contract(w)
                if contracts is None:
                    continue
                for x in contracts:
                    self.write_precontract(x)

    def clean_data(self):
        """
        Cleans all data of escape sequences.
        """
        files = os.listdir("data/raw")
        for file in files:
            if file.startswith("."):
                continue
            self.clean_file(f"data/raw/{file}", f"data/clean/{file}")
    
    def clean_file(self, file_path, new_file_path=None):
        """
        Reads a file, cleans its content, and writes the cleaned data back.
        Optionally, writes to a new file if a new file path is provided.

        Args:
        file_path (str): The path to the file to be cleaned.
        new_file_path (str, optional): The path to save the cleaned data to. If not specified, 
        it will overwrite the original file.
        """
        def clean_text(text):
            # Replace newlines and tabs with a single space
            text = json.loads(text)
            for i in range(len(text)):
                text[i]["military_branch"] = text[i]["military_branch"].replace('\n', '').replace('\t', '').replace('\r', '')
                text[i]["source_url"] = text[i]["source_url"].replace('\n', '').replace('\t', '').replace('\r', '')
                text[i]["contract_text"] = text[i]["contract_text"].replace('\n', '').replace('\t', '').replace('\r', '')
            return json.dumps(text)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        cleaned_content = clean_text(content)
        output_file_path = new_file_path if new_file_path else file_path
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)