from pydantic import BaseModel, Field
from typing import Optional, Literal

class TSysUnitsInsert(BaseModel):
    id: Optional[str] = None # reason: frontend sends an empty string
    name: str
    abbreviation: str
    type: Literal['length', 'mass', 'volume', 'time', 'amount']
    created_by: Optional[str] = None

class TSysUnitsDelete(BaseModel):
    id: int = Field(..., gt=0)
    name: str
    abbreviation: str
    type: Literal['length', 'mass', 'volume', 'time', 'amount']
    created_by: Optional[str] = None