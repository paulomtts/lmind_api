from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

from fastapi import HTTPException, status

# TSYS
class UnitObject(BaseModel):
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

class TSysUnitInsert(BaseModel):
    unit: UnitObject

class TSysUnitDelete(BaseModel):
    id: int = Field(..., gt=0)


class TSysCategoriesInsert(BaseModel):
    name: str
    description: str
    reference: str
    status: Optional[bool] = True

    @validator('name', 'description', 'reference')
    def name_must_not_be_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        return value
    
    @validator('reference')
    def reference_must_be_valid(cls, value):
        if value not in ['units', 'products-category', 'products-subcategory']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Reference must be one of the following: product, resource, task.',
            )
        return value
        
class TSysCategoriesChangeStatus(BaseModel):
    id: int = Field(..., gt=0)
    status: bool


class ProductTagObject(BaseModel):
    id: Optional[int] = None
    category: str
    registry_counter: int
    produced_counter: Optional[int] = 0
    subcategory: Optional[str] = None

class NodeObject(BaseModel):
    id: Optional[int] = None
    id_object: Optional[int] = None
    reference: Optional[str] = None
    type: str
    uuid: str
    layer: int
    position: dict[str, int]
    ancestors: list

class EdgeObject(BaseModel):
    id: Optional[int] = None
    id_object: Optional[int] = None
    reference: Optional[str] = None
    source_uuid: str
    target_uuid: str
    type: str

class RouteData(BaseModel):
    id_tag: Optional[int] = None
    id_task: int
    node_uuid: str

class TSysRouteUpsert(BaseModel):
    tag: ProductTagObject
    nodes: list[NodeObject]
    edges: Optional[list[EdgeObject]]
    routes_data: list[RouteData]


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
    id_skill_list: set[int]
    keyword_list: set[str]

class TProdResourceDelete(BaseModel):
    id: int = Field(..., gt=0)


class TaskObject(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    duration: float
    id_unit: int
    interruptible: Optional[bool] = False
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    @validator('name', 'description', 'duration', 'id_unit', 'interruptible')
    def must_not_be_empty(cls, value):
        if value == None or value == '':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Required fields must not be empty.',
            )
        return value

class TProdTaskUpsert(BaseModel):
    task: TaskObject
    id_skill_list: set[int]
    keyword_list: set[str]

class TProdTaskDelete(BaseModel):
    id: int = Field(..., gt=0)


class TProdProductTagCheckAvailability(BaseModel):
    category: str
    registry_counter: int

class TProdProductTagInsert(BaseModel):
    id_category: int
    registry_counter: Optional[int] = None
    produced_counter: Optional[int] = None
    id_product: Optional[int] = None
