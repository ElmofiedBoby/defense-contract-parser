import json
from pathlib import Path
from config import Config

class DataProcessor:
    def __init__(self, tokenizer=None, config: Config=Config()):
        """ Initialize the processor with an optional tokenizer function. """
        self.tokenizer = tokenizer
        self.data_dir = config.data_dir

    def load_data(self):
        """ Load and return a list of contracts from JSON files in the specified directory. """
        contracts = []
        for json_file in Path(self.data_dir).joinpath("annotated").glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as file:
                contracts.extend(json.load(file))
        return contracts

    def preprocess(self, data):
        """ Perform cleaning and tokenization on contract data. """
        processed_data = []
        for contract in data:
            text = contract.get('contract_text', '')
            text = self.clean_text(text)
            if self.tokenizer:
                text = self.tokenizer(text)  # Tokenize if tokenizer is provided
            processed_data.append({
                'text': text,
                'labels': {
                    'contract_id': contract.get('contract_id', ''),
                    'federal_agency': contract.get('federal_agency', ''),
                    'contract_amount': contract.get('contract_amount', 0),
                    'company_name': contract.get('company_name', ''),
                    'location': contract.get('location', ''),
                    'contract_description': contract.get('contract_description', ''),
                    'estimated_completion_date': contract.get('estimated_completion_date', ''),
                    'funds_obligated': contract.get('funds_obligated', ''),
                }
            })
        return processed_data
    
    def get_train_test_data(self, data, test_size=0.2):
        import random
        """Split data into training and testing sets."""
        random.shuffle(data)  # Shuffle the data to ensure randomness
        split_index = int(len(data) * (1 - test_size))
        train_data = data[:split_index]
        test_data = data[split_index:]
        return train_data, test_data

    def clean_text(self, text):
        """ Simple text cleaning to remove unwanted characters. """
        text = text.replace('\n', ' ').replace('\r', ' ').strip()
        return text

    def get_batches(self, data, batch_size):
        """ Yield processed data in batches. """
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]
