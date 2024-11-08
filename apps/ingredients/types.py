# graphql/types.py
from strawberry import auto
from .models import Ingredient
import strawberry


@strawberry.django.type(Ingredient)
class IngredientType:
    id: auto
    name: auto
    description: auto
    unit: auto
    created_at: auto
    updated_at: auto
