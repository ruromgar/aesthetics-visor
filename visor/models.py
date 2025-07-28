from dataclasses import dataclass
from dataclasses import field
from typing import List


@dataclass
class Metadata:
    filename: str = ""
    title: str = ""
    author: str = ""
    year: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    museum: str = ""
    material: str = ""
    style: str = ""
    dimensions: str = ""
    source: str = ""
