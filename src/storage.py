import csv
import json
from typing import Dict, List

def save_to_csv(file_path: str, data: List[Dict]):
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
