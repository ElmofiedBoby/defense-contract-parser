import json
import os
from pathlib import Path


def correct_start_end():
    path = Path("data").joinpath("manual")
    files = os.listdir(path)
    for filename in files:
        full_path = path.joinpath(filename)
        with open(full_path, 'r', encoding="utf-8") as file:
            file_data = json.load(file)  # Use json.load to read json directly from file

        for contract in file_data:
            text = contract["text"]
            for entity in contract["entities"]:
                entity["start"] = text.find(entity["value"])
                entity["end"] = entity["start"] + len(entity["value"])

        with open(full_path, 'w', encoding="utf-8") as file:
            json.dump(file_data, file, indent=4)  # Use json.dump to write json directly to file

correct_start_end()
