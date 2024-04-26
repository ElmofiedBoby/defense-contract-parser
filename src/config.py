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
        You are a parser. Your job is to parse text strings into uniform data. I will give you an input that you must read and I will also give you the structure you must convert it to. It must be a direct extraction, so no paraphrasing. If you cannot find something to extract for a specific field, you can just make it an empty string. You must not talk back, the only thing you reply with should be in the form of the example output format. You will only reply with one response output. You may not add any less or any more entities. The output must be in JSON format.

        EXAMPLE INPUT:
        "HRL Laboratories LLC, Malibu, California, was awarded a $26,991,707 cost-reimbursement contract for Creating Arrays for Strategic elecTro-optical, proLiferated and Exquisite (CASTLE) program. Work will be performed in Malibu, California, and is expected to be completed by July 19, 2029. The Air Force Research Laboratory, Kirtland Air Force Base, New Mexico, is the contracting activity (FA9453-24-C-X011)."

        EXAMPLE OUTPUT:
        {
            "text": "HRL Laboratories LLC, Malibu, California, was awarded a $26,991,707 cost-reimbursement contract for Creating Arrays for Strategic elecTro-optical, proLiferated and Exquisite (CASTLE) program. Work will be performed in Malibu, California, and is expected to be completed by July 19, 2029. The Air Force Research Laboratory, Kirtland Air Force Base, New Mexico, is the contracting activity (FA9453-24-C-X011).",
            "entities": [
                            {
                                "type": "company_name",
                                "value": "HRL Laboratories LLC",
                                "start": 0,
                                "end": 19
                            },
                            {
                                "type": "location",
                                "value": "Malibu, California",
                                "start": 21,
                                "end": 38
                            },
                            {
                                "type": "contract_amount",
                                "value": "$26,991,707",
                                "start": 51,
                                "end": 62
                            },
                            {
                                "type": "contract_description",
                                "value": "cost-reimbursement contract for Creating Arrays for Strategic elecTro-optical, proLiferated and Exquisite (CASTLE) program",
                                "start": 63,
                                "end": 192
                            },
                            {
                                "type": "estimated_completion_date",
                                "value": "July 19, 2029",
                                "start": 224,
                                "end": 237
                            },
                            {
                                "type": "federal_agency",
                                "value": "Air Force Research Laboratory",
                                "start": 265,
                                "end": 293
                            },
                            {
                                "type": "contract_id",
                                "value": "FA9453-24-C-X011",
                                "start": 341,
                                "end": 357
                            }
                        ]
            }

    '''
    )
