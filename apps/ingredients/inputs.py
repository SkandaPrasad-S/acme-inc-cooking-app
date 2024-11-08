# graphql/inputs.py
import strawberry


@strawberry.input
class IngredientInput:
    name: str
    description: str
    unit: str
