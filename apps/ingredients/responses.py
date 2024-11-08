# graphql/responses.py
import strawberry
from typing import Optional
from .types import IngredientType


@strawberry.type
class IngredientError:
    message: str
    code: str


@strawberry.type
class IngredientResponse:
    success: bool
    ingredient: Optional[IngredientType] = None
    error: Optional[IngredientError] = None
