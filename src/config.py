from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

@dataclass
class Config:

    load_dotenv()

    key: str = field(default=os.getenv('KEY'))
    base_url: str = field(default="https://www.defense.gov/News/Contracts/")
    data_dir: str = field(default="data")
    date_format: str = field(default="%B %d, %Y")
    headers: dict = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    })
    prompt: str = field(default=
    '''
        You are a parser. Your job is to parse text strings into uniform data. I will give you an input that you must read and I will also give you the structure you must convert it to. You must do this. You must not talk back, the only thing you reply with should be the example output format. You will only reply with one response output. The output must be in JSON format.

        EXAMPLE INPUT:
        "Lockheed Martin Rotary and Mission Systems, Owego, New York, was awarded a $88,380,255 Captains of Industry contract for the overhaul of B-2 digital receiver and legacy defense message system. This contract provides for overhaul, management, and material lay-in. Work will be performed at Owego, New York, and is expected to be completed by April 16, 2034. This contract was a sole source acquisition. No funds are being obligated at time of award. The Air Force Sustainment Center, Tinker Air Force Base, Oklahoma, is the contracting activity (FA8119-24-D-0008). (Awarded April 17, 2024)"

        EXAMPLE OUTPUT:
        {
            "contract_id": "FA8119-24-D-0008",
            "federal_agency": "Air Force Sustainment Center, Tinker Air Force Base, Oklahoma",
            "contract_amount": "$88,380,255",
            "company_name": "Lockheed Martin Rotary and Mission Systems",
            "location": "Owego, New York",
            "contract_description": "Captains of Industry contract for the overhaul of B-2 digital receiver and legacy defense message system. This contract provides for overhaul, management, and material lay-in.",
            "estimated_completion_date": "April 16, 2034",
            "funds_obligated": "No funds are being obligated at time of award"
        }

    '''
    )
