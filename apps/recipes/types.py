from typing import List
import strawberry
from strawberry import auto

from .models import Recipe, RecipeIngredient
from apps.ingredients.types import IngredientType


@strawberry.type
class RecipeIngredientType:
    id: int
    quantity: float
    notes: str
    ingredient: IngredientType


@strawberry.django.type(Recipe)
class RecipeType:
    id: auto
    name: auto
    description: auto
    instructions: auto
    cooking_time: auto
    created_at: auto
    updated_at: auto
    
    @strawberry.field
    def ingredients(self) -> List[RecipeIngredientType]:
        return RecipeIngredient.objects.filter(recipe=self)
    
    @strawberry.field
    def ingredient_count(self) -> int:
        return self.ingredient_count
