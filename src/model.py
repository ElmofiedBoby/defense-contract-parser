from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Contract:
    contract_id: str
    federal_agency: str
    military_branch: str
    contract_amount: float
    contract_date: date
    company_name: str
    location: str
    contract_description: str
    estimated_completion_date: date
    funds_obligated: float
    source_url: str

@dataclass
class Precontract:
    military_branch: str
    source_url: str
    contract_text: str
    contract_date: date