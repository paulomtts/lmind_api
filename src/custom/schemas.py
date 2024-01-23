from src.core.schemas import DeleteFilters

from pydantic import BaseModel
from typing import Optional, Literal

class TSysSymbolsUpsert(BaseModel):
    id: Optional[str] = None
    name: str
    abbreviation: str
    base: int
    type: Literal['length', 'mass', 'volume', 'time', 'ammount', 'paulo']
    created_by: Optional[str] = None