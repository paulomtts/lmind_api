from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

from fastapi import HTTPException, status

# TSYS
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

class TSysUnitInsert(TSysUnitsBase):
    pass

class TSysUnitDelete(TSysUnitsBase):
    id: int = Field(..., gt=0)


class TSysProductTagInsert(BaseModel): # THIS IS AN EXAMPLE
    code_a: Optional[str] = None
    counter_a: Optional[int] = None
    counter_b: Optional[int] = None


# TPROD
class TProdSkillUpsert(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('name', 'description')
    def name_must_not_be_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        return value

class TProdSkillDelete(BaseModel):
    id: int = Field(..., gt=0)




class ResourceObject(BaseModel):
    id: Optional[int] = None
    name: str
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('name')
    def name_must_not_be_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        return value

class TProdResourceUpsert(BaseModel):
    resource: ResourceObject
    id_skill_list: list[int]

class TProdResourceDelete(BaseModel):
    id: int = Field(..., gt=0)


class TProdTaskUpsert(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    duration: float
    id_unit: int
    interruptible: Optional[bool] = False
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('name', 'description', 'duration', 'id_unit', 'interruptible')
    def name_must_not_be_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        return value

class TProdTaskDelete(BaseModel):
    id: int = Field(..., gt=0)