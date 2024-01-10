# This area is meant for complex queries that are not covered by simple usage of models as
# statements. Therefore, expressions are used to create the queries. The queries are then
# imported into the CRUD router for use.

from sqlmodel import select, func, literal, case
from src.core.models import Units


# These queries allow for a single table to exhibit all ingredients, including those that are not part of the recipe
# while also allowing for the recipe ingredients to be quantified. The division between three states is necessary
# to allow for state comparisons. One for when no Recipe is selected, another for when a recipe has been clicked,
# and the last to compare updates to the recipe ingredients.

# inser queries here