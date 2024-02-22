from fastapi import Response
from fastapi.responses import JSONResponse
from sqlalchemy import inspect
from sqlalchemy.orm.exc import StaleDataError

from src.schemas import APIOutput, WhereConditions
from src.start import db

from typing import List, Union
from functools import wraps
from collections import namedtuple

import pandas as pd
import datetime
import json


# Decorators
def api_output(func):
    """
    Expects a DBOutput for `func` return value. This decorator uses APIOutput 
    to validate and parse the data. Afterwards, the data is fit it into a JSONResponse.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        data, status, message = func(*args, **kwargs)
        output = APIOutput(data=data, message=message)

        if status in [204, 304]:
            return Response(status_code=status, headers={'message': output.message})

        return JSONResponse(status_code=status, content={'data': output.data, 'message': output.message})
    return wrapper


# CRUD
def append_userstamps(table_cls, data: Union[List[dict], dict, pd.DataFrame], id_user: str) -> list[dict]:
    """
    Appends the user ID to the data.
    """

    def set_stamps(row: Union[dict, pd.Series], mode: str):
        table_columns = [col.name for col in table_cls.__table__.columns]


        if mode == 'insert':
            if 'created_by' in table_columns:
                row['created_by'] = id_user
            
        if 'updated_by' in table_columns:
            row['updated_by'] = id_user

        if mode == 'update': 
            row.pop('created_by', None)
            row.pop('created_at', None)


    inspector = inspect(table_cls)
    pk_columns = [pk.name for pk in inspector.primary_key]
    mode = 'update'

    if isinstance(data, list) and all(isinstance(row, dict) for row in data):
        for row in data:
            if not any(row.get(pk) for pk in pk_columns): mode = 'insert'
            set_stamps(row, mode)

    elif isinstance(data, pd.DataFrame):
        for _, row in data.iterrows():
            if not any(row.get(pk) for pk in pk_columns): mode = 'insert'
            set_stamps(row, mode)

    elif isinstance(data, dict):
        if not any(data.get(pk) for pk in pk_columns): mode = 'insert'
        set_stamps(data, mode)

def append_timestamps(data: Union[List[dict], dict, pd.DataFrame]) -> list[dict]:
    """
    Appends the current timestamp to the data.
    """

    if isinstance(data, list) and all(isinstance(row, dict) for row in data):
        for row in data:
            if 'created_at' in row.keys() and not row.get('created_at'):
                row['created_at'] = datetime.datetime.utcnow()

            if 'updated_at' in row.keys():
                row['updated_at'] = datetime.datetime.utcnow()

    elif isinstance(data, dict):
        if 'created_at' in data.keys() and not data.get('created_at'):
            data['created_at'] = datetime.datetime.utcnow()

        if 'updated_at' in data.keys():
            data['updated_at'] = datetime.datetime.utcnow()

    elif isinstance(data, pd.DataFrame):
        if 'created_at' in data.columns:
            data['created_at'].fillna(datetime.datetime.utcnow(), inplace=True)

        if 'updated_at' in data.columns:
            data['updated_at'] = datetime.datetime.utcnow()
    else:
        raise TypeError(f"Could not append timestamps. Current data type {type(data)} is not supported.")

    return data


# Verifications
def check_stale_data(table_cls, filters: WhereConditions, reference: str) -> pd.DataFrame:
    """
    Check if the data is stale.
    """
    curr_data = db.query(table_cls, None, filters)

    is_greater = (curr_data['updated_at'] > reference).any()
    if is_greater:
        raise StaleDataError("This data has been updated by another user. Please refresh the page and try again.")

    return curr_data   


# Dataframe state comparison
def find_common(df1: pd.DataFrame, df2: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Finds the common rows between two dataframes by comparing the values of the specified columns.

    Args:
        df1 (pd.DataFrame): The first dataframe.
        df2 (pd.DataFrame): The second dataframe.
        cols (list[str]): The columns to compare.

    Returns:
        pd.DataFrame: The common rows between the two dataframes.
    """
    df1 = df1[cols]
    df2 = df2[cols]
    df = df1.merge(df2, on=cols, how='inner')

    return df


def find_missing(df1: pd.DataFrame, df2: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Finds the missing rows between two dataframes by comparing the values of the specified columns.

    Args:
        df1 (pd.DataFrame): The first dataframe.
        df2 (pd.DataFrame): The second dataframe.
        cols (list[str]): The columns to compare.

    Returns:
        pd.DataFrame: The missing rows between the two dataframes.
    """
    df1 = df1[cols]
    df2 = df2[cols]
    df = df1.merge(df2, on=cols, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

    return df


def find_new(df1: pd.DataFrame, df2: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Finds the new rows between two dataframes by comparing the values of the specified columns.

    Args:
        df1 (pd.DataFrame): The first dataframe.
        df2 (pd.DataFrame): The second dataframe.
        cols (list[str]): The columns to compare.

    Returns:
        pd.DataFrame: The new rows between the two dataframes.
    """
    df1 = df1[cols]
    df2 = df2[cols]
    df = df1.merge(df2, on=cols, how='outer', indicator=True).query('_merge == "right_only"').drop('_merge', axis=1)
    
    return df
