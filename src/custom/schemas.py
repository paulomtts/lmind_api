from src.core.schemas import DeleteFilters

from pydantic import BaseModel
from typing import List


class CSTUpsertRecipe(BaseModel):
    reference_time: str
    form_data: dict[str, str]
    recipe_ingredients_rows: List[dict]


class CSTDeleteRecipeInput(BaseModel):
    recipe: DeleteFilters
    composition: DeleteFilters
