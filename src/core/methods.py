from fastapi.responses import JSONResponse
from fastapi import Response
from sqlalchemy.orm.exc import StaleDataError

from src.core.schemas import APIOutput, WhereConditions
from src.core.start import db

from typing import List, Union
from functools import wraps

import pandas as pd


# Decorators
def api_output(func):
    """
    Expects a DBOutput for `func` return value. This decorator uses APIOutput 
    to validate and parse the data. Afterwards, the data is fit it into a JSONResponse.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        data, status, message = func(*args, **kwargs)
        ouput = APIOutput(data=data, message=message)

        if status in [204, 304]:
            return Response(status_code=status, headers={'message': ouput.message})

        return JSONResponse(status_code=status, content={'data': ouput.data, 'message': ouput.message})
    return wrapper


# CRUD
def append_user_credentials(data: Union[List[dict], dict, pd.DataFrame], user_id: str) -> list[dict]:
    """
    Appends the user ID to the data.
    """

    if isinstance(data, list) and all(isinstance(row, dict) for row in data):
        for row in data:
            if not row.get('created_by'):
                row['created_by'] = user_id

            row['updated_by'] = user_id

    elif isinstance(data, dict):
        if not data.get('created_by'):
            data['created_by'] = user_id

        data['updated_by'] = user_id

    elif isinstance(data, pd.DataFrame):
        if 'created_by' in data.columns:
            data['created_by'].fillna(user_id, inplace=True)
        else:
            data['created_by'] = user_id

        data['updated_by'] = user_id

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
