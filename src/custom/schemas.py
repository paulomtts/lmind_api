from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

from fastapi import HTTPException, status

class TSysUnitsBase(BaseModel):
    name: str
    abbreviation: str
    type: str
    created_by: Optional[str] = None

    @validator('name', 'abbreviation')
    def name_must_not_be_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        return value
    
    @validator('type')
    def type_must_be_valid(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        if value not in ['length', 'mass', 'volume', 'time', 'amount']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Type must be one of the following: length, mass, volume, time, amount.',
            )
        return value

class TSysUnitsInsert(TSysUnitsBase):
    pass

class TSysUnitsDelete(TSysUnitsBase):
    id: int = Field(..., gt=0)

class TSysProductTagInsert(BaseModel): # THIS IS AN EXAMPLE
    code_a: Optional[str] = None
    counter_a: Optional[int] = None
    counter_b: Optional[int] = None