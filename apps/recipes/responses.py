from typing import Optional
import strawberry

from .types import RecipeType


@strawberry.type
class RecipeError:
    message: str
    code: str


@strawberry.type
class RecipeResponse:
    success: bool
    recipe: Optional[RecipeType] = None
    error: Optional[RecipeError] = None
