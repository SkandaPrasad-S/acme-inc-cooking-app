from typing import Optional, List
import strawberry

@strawberry.input
class RecipeIngredientInput:
    ingredient_id: int
    quantity: float
    notes: Optional[str] = ""


@strawberry.input
class RecipeInput:
    name: str
    description: str
    instructions: str
    cooking_time: int
    ingredients: List[RecipeIngredientInput]


@strawberry.input
class BulkUpdateRecipeIngredientInput:
    ingredient_id: int
    quantity: float
    notes: Optional[str] = ""
