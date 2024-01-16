from pydantic import BaseModel, validator
from typing import List, Any, Optional, Literal

import pandas as pd
import json

class TableNames(BaseModel):
    table_name: Literal['tsys_symbols'] \
              | Literal['tsys_categories'] \

    @validator('table_name')
    def validate_table_name(cls, value):
        try:
            if value not in [
            'tsys_symbols'
            , 'tsys_categories'
        ]:
                raise ValueError(f"Invalid table name.")
        except ValueError as e:
            print(e)
            
        return value
    
class WhereConditions(BaseModel):
    or_: Optional[dict[str, List[str | int]]] = {}
    and_: Optional[dict[str, List[str | int]]] = {}
    like_: Optional[dict[str, List[str | int]]] = {}
    not_like_: Optional[dict[str, List[str | int]]] = {}

    def __iter__(self):
        yield self.or_
        yield self.and_
        yield self.like_
        yield self.not_like_

class DeleteFilters(BaseModel):
    field: str
    values: List[str | int]

class SuccessMessages(BaseModel):
    client: Optional[str] = 'Operation was successful.'
    logger: Optional[str] = None

    def __init__(self, client: str = None, logger: str = None):
        super().__init__(client=client, logger=logger)


class CRUDInsertInput(TableNames, BaseModel):
    data: list

class CRUDSelectInput(TableNames, BaseModel):
    filters: Optional[WhereConditions] = WhereConditions()
    lambda_kwargs: Optional[dict[str, Any]] = {}

class CRUDUpdateInput(TableNames, BaseModel):
    data: dict

class CRUDDeleteInput(TableNames, BaseModel):
    filters: Optional[WhereConditions]


class DBOutput(BaseModel):
    """
    The purpose of this class is to make it easier to understand the layers of the API.
    """

    data: List[dict] | pd.DataFrame | Any
    status: int
    message: str

    class Config:
        arbitrary_types_allowed = True

    def __iter__(self):
        yield self.data
        yield self.status
        yield self.message

class APIOutput(BaseModel):
    """
    Outputs the data and message of the operation. All data is converted to JSON strings.
    """

    data: str | dict[str, str]
    message: str

    def __init__(self, data: List[dict] | pd.DataFrame, message: str):
        data = self.to_json(data)
        super().__init__(data=data, message=message)

    def __iter__(self):
        yield self.data
        yield self.message

    def to_json(self, data):
        """
        Converts the data content to JSON strings.
        """
        if isinstance(data, pd.DataFrame): # CRUD non-specific
            return data.to_json(orient='records')
        elif hasattr(data, '_asdict'): # Custom with single=true
            return json.dumps(data._asdict())
        elif isinstance(data, dict): # Custom dict
            parsed_data = {}

            for key, data in data.items():
                if isinstance(data, pd.DataFrame):
                    parsed_data[key] = data.to_json(orient='records')
                elif hasattr(data, '_asdict'):
                    parsed_data[key] = json.dumps(data._asdict())
                else:
                    parsed_data[key] = json.dumps(data)

            return parsed_data
        return data
