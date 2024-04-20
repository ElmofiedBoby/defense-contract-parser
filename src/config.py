from dataclasses import dataclass, field

@dataclass
class Config:
    base_url: str = field(default="https://www.defense.gov/News/Contracts/")
    data_dir: str = field(default="data")
    date_format: str = field(default="%B %d, %Y")
    headers: dict = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    })